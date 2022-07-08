from collections import Counter
from pbreader import ProtobufReader, RawTag
from reader import FileSection

class Schema:
    def __init__(self, schema):
        self.schema = { 'structures':[ {'name':'$discostat', 'factory':DiscoveryStat, 'fields':{'$raw':{'setter':DiscoveryStat.addraw}}} ] }
        self.merge(schema)

    def start(self):
        return self.getstructure(self.schema['start'])

    def getstructure(self, name):
        return self.index[name]

    def merge(self, schema):
        old = self.schema
        self.schema = schema
        self.index = {}
        for s in self.schema['structures']:
            self.index[s['name']] = s
        for s in old['structures']:
            if s['name'] not in self.index:
                self.index[s['name']] = s
                self.schema['structures'].append(s)

class SchemaReader:
    def __init__(self, datafile, schema):
        self.datafile = datafile
        self.schema = schema

    def makereader(self):
        start = self.schema.start()
        result = None
        if 'factory' in start:
             result = start['factory']()
        reader = ProtobufReader(self.datafile, self.schema, start['fields'], data = result)
        return reader

    def read(self):
        reader = self.makereader()
        reader.read()
        return reader.data

    def readsection(self, pos, size):
        reader = self.makereader()
        reader.readsection(FileSection(self.datafile, pos, size))
        return reader.data

class DiscoveryStat:
    def __init__(self):
        self.counter = Counter()

    def addraw(self, tag):
        self.counter[ (tag.fieldno, tag.wiretype) ] += 1

    def prettyprint(self, indent):
        buf = ''
        for tag in sorted(self.counter):
            buf += "{0}{1} ({2}): {3} times\n".format(indent, tag[0], RawTag.wiretypes()[tag[1]], self.counter[tag])
        return buf