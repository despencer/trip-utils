import logging
import math
from datetime import datetime, timedelta
from schemareader import Schema, SchemaReader
from pbreader import ProtobufReader, RawReader
import geo

def unixtime(x):
    return datetime(1970,1,1)+timedelta(milliseconds=x)

# Top level object. original ObfInfo, proto OsmAndStructure. Loader ObfReader_P::readInfo
class Map:
    def __init__(self):
        self.version = None
        self.sections = []

    def locatenodes(self, zoom, bounds):
        nodes = []
        for s in self.sections:
           for ml in s.maplevels:
                if ml.minzoom <= zoom and zoom <= ml.maxzoom:
                     nodes.extend( ml.node.locatenodes(bounds, s) )
        return nodes

    def locateobjects(self, zoom, bounds):
        objects = {}
        for (node, section) in self.locatenodes(zoom, bounds):
            node.block.locateobjects(objects, bounds, section)
        return objects

# A portion of a map, typically administrative region. original ObfMapSectionInfo. proto OsmAndMapIndex. Loader ObfMapSectionReader_P::read
class Section:
    def __init__(self):
        self.name = None
        self.maplevels = []
        self.encodings = []

# Different maps for diffrent zooms. original ObfMapSectionLevel. proto OsmAndMapIndex_MapRootLevel. Loader ObfMapSectionReader::readMapLevelHeader
class MapLevel:
    def __init__(self):
        self.minzoom = None
        self.maxzoom = None
        self.ibounds = geo.Rectangle()
        self._bounds = None
        self._node = None
        self._nodereader = None

    @property
    def node(self):
        if self._nodereader != None:
            self._nodereader()
            self._nodereader = None
            self._node.adjustbounds(self.ibounds)
        return self._node

    @property
    def bounds(self):
        if self._bounds == None:
            self._bounds = geo.Rectangle()
            self._bounds.left.value = lonitod(self.ibounds.left.value)
            self._bounds.top.value = latitod(self.ibounds.top.value)
            self._bounds.right.value = lonitod(self.ibounds.right.value)
            self._bounds.bottom.value = latitod(self.ibounds.bottom.value)
        return self._bounds

# original original ObfMapSectionLevelTreeNode. proto OsmAndMapIndex_MapRootLevel.  Loader ObfMapSectionReader::loadMapObjects/readMapLevelTreeNodes
# children - original ObfMapSectionLevelTreeNode. proto OsmAndMapIndex_DataBox. loader ObfMapSectionReader::readTreeNodeChildren/readTreeNode
class MapNode:
    def __init__(self):
        self.ibounds = geo.Rectangle()
        self.bounds = geo.Rectangle()
        self._children = []
        self._childrenreader = []
        self._block = None
        self._blockreader = None

    @property
    def children(self):
        if len(self._childrenreader) > 0:
            for cr in self._childrenreader:
                cr()
            self._childrenreader.clear()
            for c in self._children:
                c.adjustbounds(self.ibounds)
        return self._children

    @property
    def block(self):
        if self._blockreader != None:
            self._blockreader()
        return self._block

    def readblockptr(self, tag):
        offset, size = tag.reader.read_fixed(4, 'big')
        logging.debug('Tree node {0:X} limit {1:X}, tag {2:X}, value {3:X}, final {4:X}'.format(tag.reader.pos, tag.reader.limit, tag.pos, offset, tag.reader.pos+offset))
        self._blockreader = lambda: self.readblock(tag.reader.pbf, offset + tag.reader.pos)
        return (size, False)

    def readblock(self, pbf, offset):
        amount, size = RawReader.read_varint_frompbf(pbf, offset)
        schema = Schema(blockschema)
        reader = SchemaReader(pbf, schema)
        self._block = reader.readsection(offset+size, amount)
        self._block.adjustobjects(self.ibounds)

    def adjustbounds(self, parent):
        self.ibounds.left.value += parent.left.value
        self.ibounds.top.value += parent.top.value
        self.ibounds.right.value += parent.right.value
        self.ibounds.bottom.value += parent.bottom.value
        self.bounds.left.value = lonitod(self.ibounds.left.value)
        self.bounds.top.value = latitod(self.ibounds.top.value)
        self.bounds.right.value = lonitod(self.ibounds.right.value)
        self.bounds.bottom.value = latitod(self.ibounds.bottom.value)

    def locatenodes(self, bounds, section):
        if not self.bounds.isintersects(bounds):
            return []
        if self.block != None:
            return [ (self,section) ]
        nodes = []
        for c in self.children:
            nodes.extend( c.locatenodes(bounds, section) )
        return nodes

class MapBlock:
    def __init__(self):
        self.baseId = None
        self.objects = []
        self.strings = None

    def adjustobjects(self, nodebounds):
        mask = ~31
        left = nodebounds.left.value & mask
        top = nodebounds.top.value & mask
        for o in self.objects:
            if o.coordinates != None:
                coords = []
                for i in range(0, len(o.coordinates), 2):
                    left += o.coordinates[i] << 5
                    top += o.coordinates[i+1] << 5
                    coords.append( geo.Point.fromlatlon(latitod(top), lonitod(left)) )
                o.coordinates = coords

    def locateobjects(self, objects, bounds, section):
        for o in self.objects:
            if o.id not in objects and o.isinside(bounds):
                o.expandattr(section)
                if o.mapattr != None:
                    objects[o.id] = o

class MapObject:
    def __init__(self):
        self.id = None
        self.coordinates = None
        self.types = None
        self.mapattr = None

    def isinside(self, bounds):
        if self.coordinates == None:
            return False
        for c in self.coordinates:
            if bounds.isinside(c):
                return True
        return False

    def expandattr(self, section):
        if self.mapattr == None and self.types != None:
           self.mapattr = []
           for t in self.types:
                self.mapattr.append(section.encodings[t+1])

class StringTable:
    def __init__(self):
        self.table = []

class Attribute:
    def __init__(self):
        self.tag = None
        self.value = None

    def __repr__(self):
        return '{0}={1}'.format(self.tag, self.value)

obschema = { 'start':'header', 'structures':[
        { 'name':'header', 'factory': Map, 'fields':
    { 1 : { 'name':'version' }, 18:{'name':'creation', 'factory':unixtime},
    6:{ 'name':'sections', 'factory':Section, 'children':{     # map_section
        2:{'name':'name', 'factory':ProtobufReader.readutf8},
        4:{'name':'encodings', 'structure':'attribute'},
        5:{'name':'maplevels', 'structure':'maplevel' } } } } },
    { 'name':'maplevel', 'factory':MapLevel, 'fields':{
            1:{'name':'maxzoom'}, 2:{'name':'minzoom'}, 3:{'name':'ibounds.left.value'}, 4:{'name':'ibounds.right.value'}, 5:{'name':'ibounds.top.value'}, 6:{'name':'ibounds.bottom.value'},
            7:{'name':'_node', 'lazy':'_nodereader', 'structure':'treenode' } } },
    { 'name':'treenode', 'factory':MapNode, 'fields': {
        1:{'name':'ibounds.left.value', 'factory':ProtobufReader.readzigzag}, 2:{'name':'ibounds.right.value', 'factory':ProtobufReader.readzigzag},
        3:{'name':'ibounds.top.value', 'factory':ProtobufReader.readzigzag}, 4:{'name':'ibounds.bottom.value', 'factory':ProtobufReader.readzigzag},
        5:{'name':'_blockoffset', '$raw':MapNode.readblockptr}, 7:{'name':'_children', 'lazy':'_childrenreader','structure':'treenode'} }},
    { 'name':'attribute', 'factory':Attribute, 'fields': {
        3:{'name':'tag', 'factory':ProtobufReader.readutf8}, 5:{'name':'value', 'factory':ProtobufReader.readutf8} }} ] }

blockschema = { 'start':'mapblock', 'structures':[
    { 'name':'mapblock', 'factory':MapBlock, 'fields':{10:{'name':'baseId'}, 12:{'name':'objects', 'structure':'mapobject'},
        15:{'name':'strings','structure':'stringtable'} } },
    { 'name':'mapobject', 'factory':MapObject, 'fields': { 
        1:{'name':'coordinates', 'factory':(lambda x:ProtobufReader.readvarintarray(x, ProtobufReader.readzigzag)) },
        7:{'name':'types', 'factory':(lambda x:ProtobufReader.readvarintarray(x, (lambda x:x) )) },
        12:{'name':'id'}  }},
    { 'name':'stringtable', 'factory':StringTable, 'fields':{1:{'name':'table', 'factory':ProtobufReader.readutf8} } }  ] }

# longitude from integer to degrees
def lonitod(x):
    return (x * 360.0 / (1024.0 * (1<<21))) - 180.0

def latitod(y):
    sign = -1 if y < 0 else 1
    arg = math.pi * ( 1.0 - ( y / (512.0 * (1<<21))  ) )
    return math.atan(sign * math.sinh(arg)) * 180.0 / math.pi

def readobf(obfile):
    schema = Schema(obschema)
    reader = SchemaReader(obfile, schema)
    return reader.read()

