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

class SchemaReader:
    def __init__(self, datafile, schema):
        self.datafile = datafile
        self.schema = Schema(schema)

    def read(self):
        reader = ProtobufReader(self.datafile, self.schema, self.schema.start()['fields'])
        reader.read()
