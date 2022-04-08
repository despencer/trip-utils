#!/usr/bin/python3

from collections import Counter
import os
import logging

class RawSection:
    def __init__(self, pbf, pos, size):
        self.pbf = pbf
        self.pos = pos
        self.size = size

    def __repr__(self):
       return 'Section at {0:X} of size {1:X}'.format(self.pos, self.size)

class RawTag:
    def __init__(self, reader, pos, fieldno, wiretype):
        self.reader = reader
        self.pos = pos
        self.fieldno = fieldno
        self.wiretype = wiretype

    def section(self, delta, size):
        sect = RawSection(self.reader.pbf, self.pos + delta, size)
        return sect

class RawReader:
    def __init__(self):
        pass

    @classmethod
    def fromfile(cls, pbf):
        reader = cls()
        reader.pbf = pbf
        reader.pos = 0
        reader.pbf.seek(0, os.SEEK_END)
        reader.limit = reader.pbf.tell()
        reader.pbf.seek(0)
        return reader

    @classmethod
    def fromsection(cls, section):
        reader = cls()
        reader.pbf = section.pbf
        reader.pos = section.pos
        reader.limit = section.pos + section.size
        return reader

    def readfilter(self, handler):
        pos = self.pos
        stop = False
        while True:
            if pos >= self.limit or stop:
                return
            self.pbf.seek(pos)
            desc, size = self.read_varint()
            logging.debug('read tag %s type %s', desc>>3, desc&0x7)
            payload, stop = handler( RawTag(self, pos+size, desc>>3, desc&0x7 ) )
            pos = pos + size + payload

    def readtags(self, handlers):
        self.readfilter( lambda tag: handlers[tag.fieldno](tag) )

    def read_varint(self):
        size = 0
        value = 0
        while True:
            chunk = self.pbf.read(1)[0]
            value = ( ( chunk & 0x7F ) << ( size * 7) ) | value
            size = size + 1
            if (chunk & 0x80) == 0:
                return (value, size)

    def read_fixed(self, size, byteorder):
        return ( int.from_bytes( self.pbf.read(size), byteorder), size)

    def read_sequence(self):
        amount, size = self.read_blobamount(2)
        return (None, size + amount)

    def read_blobamount(self, wiretype):
        if wiretype == 6:
            return self.read_fixed(4, 'big')
        else:
            return self.read_varint()

    def read_blob(self):
        amount, size = self.read_blobamount(6)
        return (None, size + amount)

    def read_varintvalue(self, tag):
        value, size = self.read_varint()
        return (size, False)

    def readvalue_bywiretype(self, tag):
        handlers = { 0:self.read_varint, 1:lambda: self.read_fixed(8, 'little'), 2:self.read_sequence,
            5:lambda: self.read_fixed(4, 'little'), 6:self.read_blob }
        if tag.wiretype in handlers:
            return handlers[tag.wiretype]()
        return (0, 0)

    def read_bywiretype(self, tag):
        value, size = self.readvalue_bywiretype(tag)
        if size == 0:
            return (0, True)
        return (size, False)

class ProtobufReader:
    def __init__(self, pbf, pbschema, pbstr, data = None):
        self.pbf = pbf
        self.pbschema = pbschema
        self.pbstr = pbstr
        self.indent = ''
        self.printing = False
        self.counter = Counter()
        self.data = data

    def read(self):
        reader = RawReader.fromfile(self.pbf)
        reader.readfilter(self.handler)

    def readsection(self, section):
        reader = RawReader.fromsection(section)
        reader.readfilter(self.handler)

    def handler(self, tag):
        if tag.fieldno not in self.pbstr:
            return tag.reader.read_bywiretype(tag)
        self.counter[tag.fieldno] += 1
        tagstr = self.pbstr[tag.fieldno]
        if tag.wiretype in (2, 6):
            return self.handleblob(tag, tagstr)
        else:
            return self.handlesimple(tag, tagstr)

    def handleblob(self, tag, tagstr):
        amount, size = tag.reader.read_blobamount(tag.wiretype)
        value = None
        if not ('children' in tagstr or 'structure' in tagstr):
            if 'factory' in tagstr:
                value = tagstr['factory'](self.pbf.read(amount))
        else:
            if 'children' in tagstr:
                if 'factory' in tagstr:
                    value = tagstr['factory']()
            else:
                structure = self.pbschema.getstructure(tagstr['structure'])
                if 'factory' in structure:
                    value = structure['factory']()
        if value != None:
            self.addattr(tagstr, value)
        self.handleprint(value, tag, tagstr)
        if 'children' in tagstr or 'structure' in tagstr:
            if 'children' in tagstr:
                fields = tagstr['children']
            else:
                fields = self.pbschema.getstructure(tagstr['structure'])['fields']
            section = tag.section(size, amount)
            child = ProtobufReader(self.pbf, self.pbschema, fields, data=value)
            child.indent = self.indent + '    '
            child.printing = self.printing
            if 'print' in tagstr and tagstr['print'] != self.counter[tag.fieldno]-1:
                child.printing = False
            child.readsection(section)
        return (size + amount, False)

    def handlesimple(self, tag, tagstr):
        value, size = tag.reader.readvalue_bywiretype(tag)
        obj = value
        if 'factory' in tagstr:
            obj = tagstr['factory'](value)
        self.addattr(tagstr, obj)
        self.handleprint(obj, tag, tagstr)
        return (size, False)

    def handleprint(self, obj, tag, tagstr):
        if not self.printing:
            return
        if 'print' in tagstr and tagstr['print'] != self.counter[tag.fieldno]-1:
            return
        if obj == None and 'default' in tagstr:
            obj = tagstr['default']
        if 'format' in tagstr:
            reprstr = ('{0:'+tagstr['format']+'}').format(obj)
            if 'name' in tagstr:
                reprstr = '{0}={1}'.format(tagstr['name'], reprstr)
            print('{0}{1}'.format(self.indent, reprstr))

    def addattr(self, tagstr, value):
        if self.data != None:
            name = tagstr['name']
            if hasattr(self.data, name):
                exist = getattr(self.data, name)
                if isinstance(exist, list):
                    exist.append(value)
                    return
            setattr(self.data, tagstr['name'], value)

    @classmethod
    def readutf8(cls, value):
        return value.decode('utf-8')

    @classmethod
    def readzigzag(cls, value):
        return (value>>1) ^ (-(value&1))