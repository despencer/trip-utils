#!/usr/bin/python3

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
        amount, size = self.read_varint()
        value = self.pbf.read( min(amount, 0x20) )
        return (value, size + amount)

    def read_blob(self):
        amount, size = self.read_fixed(4, 'big')
        value = self.pbf.read( min(amount, 0x20) )
        return (value, size + amount)

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
    def __init__(self, pbf, pbstr):
        self.pbf = pbf
        self.pbstr = pbstr
        self.indent = ''

    def read(self):
        reader = RawReader.fromfile(self.pbf)
        reader.readfilter(self.handler)

    def handler(self, tag):
        if tag.wiretype == 6:
            return tag.reader.read_bywiretype(tag)
        value, size = tag.reader.readvalue_bywiretype(tag)
        if tag.fieldno in self.pbstr:
            tagstr = self.pbstr[tag.fieldno]
            obj = value
            if 'factory' in tagstr:
                obj = tagstr['factory'](value)
            if 'format' in tagstr:
                reprstr = ('{0:'+tagstr['format']+'}').format(obj)
                print('{0}{1}'.format(self.indent, reprstr))
        if size == 0:
            return (0, True)
        return (size, False)
