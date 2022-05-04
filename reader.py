import os

class FileSection:
    def __init__(self, pbf, pos, size):
        self.pbf = pbf
        self.pos = pos
        self.size = size

    def __repr__(self):
       return 'Section at {0:X} of size {1:X}'.format(self.pos, self.size)

class FileReader:
    def __init__(self, datafile):
        self.datafile = datafile

    def readintat(self, pos, size, byteorder):
        self.datafile.seek(pos)
        return int.from_bytes( self.datafile.read(size), byteorder)

    def size(self):
        self.datafile.seek(0, os.SEEK_END)
        return self.datafile.tell()
