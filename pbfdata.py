import zlib
from pbreader import ProtobufReader, RawReader, unixtime
from schemareader import Schema, SchemaReader
from reader import FileReader, BytesReader

class OsmFile:
    def __init__(self):
        self.header = None
        self.blobs = []

class BlobHeader:
    def __init__(self):
        self.type = None
        self.datasize = None
        self.blob = None

class BlobBlock:
    def __init__(self):
        self.rawsize = None
        self.blobdata = None

    def setdataptr(self, tag):
        amount, size = tag.reader.read_blobamount(tag.wiretype)
        self.blobdata = tag.section(size, amount)
        return (size + amount, False)

    def readblockptr(self, tag):
        offset, size = tag.reader.read_fixed(4, 'big')
        logging.debug('Tree node {0:X} limit {1:X}, tag {2:X}, value {3:X}, final {4:X}'.format(tag.reader.pos, tag.reader.limit, tag.pos, offset, tag.reader.pos+offset))
        self._blockreader = lambda: self.readblock(tag.reader.pbf, offset + tag.reader.pos)
        return (size, False)


blobheaderschema = { 'start':'header', 'structures':[
        { 'name':'header', 'factory': BlobHeader, 'fields': {1:{'name':'type', 'factory':ProtobufReader.readutf8}, 3:{'name':'datasize'} } } ] }
blobschema = { 'start':'blob', 'structures':[
        { 'name':'blob', 'factory':BlobBlock, 'fields': {2:{'name':'rawsize'},  3:{'$raw':BlobBlock.setdataptr} } } ] }

class OsmHeader:
    def __init__(self):
        self.required = []
        self.source = None
        self.creation = None
        self.url = None

headerschema = { 'start':'header', 'structures':[
        { 'name':'header', 'factory': OsmHeader, 'fields':
            {4:{'name':'required', 'factory':ProtobufReader.readutf8}, 16:{'name':'source', 'factory':ProtobufReader.readutf8},
            32:{'name':'creation', 'factory':unixtime}, 34:{'name':'url', 'factory':ProtobufReader.readutf8} } } ] }

class OsmPbfReader:
    def __init__(self, pbfile):
        self.pbfile = pbfile
        self.osmfile = OsmFile()

    def readblobs(self):
        filereader = FileReader(self.pbfile)
        pos = 0
        limit = filereader.size()
        while True:
            if pos >= limit:
                return
            headersize = filereader.readintat(pos, 4, 'big')
            headerreader = SchemaReader(self.pbfile, Schema(blobheaderschema))
            header = headerreader.readsection(pos+4, headersize)
            blobreader = SchemaReader(self.pbfile, Schema(blobschema))
            header.blob = blobreader.readsection(pos+4+headersize, header.datasize)
            if header.type == 'OSMHeader':
                if self.osmfile.header == None:
                    self.readheader(header)
                else:
                    print('Warning: second header detected')
            else:
                self.osmfile.blobs.append(header)
            pos += 4 + headersize + header.datasize

    def readheader(self, headerblob):
        data = zlib.decompress(headerblob.blob.blobdata.read())
        bytes = BytesReader(data)
        self.osmfile.header = SchemaReader(bytes, Schema(headerschema)).read()

def readpbf(pbfile):
    reader = OsmPbfReader(pbfile)
    reader.readblobs()
    return reader.osmfile
