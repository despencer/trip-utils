from pbreader import ProtobufReader

class Schema:
    def __init__(self, schema):
        self.schema = schema
        self.index = {}
        for s in self.schema['structures']:
            self.index[s['name']] = s

    def start(self):
        return self.getstructure(self.schema['start'])

    def getstructure(self, name):
        return self.index[name]

    def addformat(self, format):
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
        reader.read()
        return result
