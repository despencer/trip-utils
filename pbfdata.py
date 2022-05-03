from pbreader import ProtobufReader, RawReader
from schemareader import Schema, SchemaReader
from reader import Reader

class OsmFile:
    def __init__(self):
        self.blobs = []

class BlobHeader:
    def __init__(self):
        self.type = None
        self.datasize = None

headerschema = { 'start':'header', 'structures':[
        { 'name':'header', 'factory': BlobHeader, 'fields': {1:{'name':'type', 'factory':ProtobufReader.readutf8}, 3:{'name':'datasize'} } } ] }

class OsmPbfReader:
    def __init__(self, pbfile):
        self.pbfile = pbfile
        self.osmfile = OsmFile()

    def readblobs(self):
        filereader = Reader(self.pbfile)
        pos = 0
        limit = filereader.size()
        while True:
            if pos >= limit:
                return
            headersize = filereader.readintat(pos, 4, 'big')
            headerreader = SchemaReader(self.pbfile, Schema(headerschema))
            header = headerreader.readsection(pos+4, headersize)
            self.osmfile.blobs.append(header)
            pos += 4 + headersize + header.datasize

def readpbf(pbfile):
    reader = OsmPbfReader(pbfile)
    reader.readblobs()
    return reader.osmfile
