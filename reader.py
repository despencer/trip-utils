import os

class Reader:
    def __init__(self, datafile):
        self.datafile = datafile

    def readintat(self, pos, size, byteorder):
        self.datafile.seek(pos)
        return int.from_bytes( self.datafile.read(size), byteorder)

    def size(self):
        self.datafile.seek(0, os.SEEK_END)
        return self.datafile.tell()
