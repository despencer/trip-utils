from schemareader import Schema, SchemaReader
from reader import Reader

pbschema = { 'start':'$discostat', 'structures':[] }

def readpbf(pbfile):
    schema = Schema(pbschema)
    rawreader = Reader(pbfile)
    headersize = rawreader.readintat(0, 4, 'big')
    reader = SchemaReader(pbfile, schema)
    return reader.readsection(4, headersize)
