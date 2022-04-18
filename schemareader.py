from collections import Counter
from pbreader import ProtobufReader, RawTag

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

    def addformat(self, format):
        if not 'format' in self.schema:
            self.schema['format']=''
        for s in self.schema['structures']:
            s['format']=''
            self.addformat_children( s['fields'] )
        for f in format['structures']:
            s = self.getstructure(f['name'])
            self.addformat_childrenspecific(s['fields'], f['fields'])

    def addformat_children(self, children):
        for v in children.values():
            v['format']=''
            if 'children' in v:
                self.addformat_children( v['children'] )

    def addformat_childrenspecific(self, children, format):
        for field, group in format.items():
            child = children[field]
            for specs, value in group.items():
                if specs == 'children':
                    self.addformat_childrenspecific(child['children'], value)
                else:
                    child[specs] = value

class SchemaReader:
    def __init__(self, datafile, schema):
        self.datafile = datafile
        self.schema = schema

    def read(self):
        start = self.schema.start()
        result = None
        if 'factory' in start:
             result = start['factory']()
        reader = ProtobufReader(self.datafile, self.schema, start['fields'], data = result)
        if 'format' in self.schema.schema:
            reader.printing = True
        reader.read()
        return result

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