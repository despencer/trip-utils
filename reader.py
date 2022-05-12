from datetime import datetime, timedelta
import os

def deltadecode(x):
    if len(x) < 2:
        return x
    p = 0
    y = []
    for i in range(0, len(x)):
        p += x[i]
        y.append(p)
    return y

class Indicator:
    def __init__(self, interval=10):
        self.start = datetime.now()
        self.interval = timedelta(seconds = interval)

    def ready(self):
        delta = datetime.now()-self.start
        if delta >= self.interval:
            self.start = datetime.now()
            return True
        return False

class FileSection:
    def __init__(self, pbf, pos, size):
        self.pbf = pbf
        self.pos = pos
        self.size = size

    def read(self):
        self.pbf.seek(self.pos)
        return self.pbf.read(self.size)

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

class BytesReader:
    def __init__(self, data):
        self.pos = 0
        self.data = data

    def read(self, size):
        ret = self.data[self.pos:self.pos+size]
        self.seek(self.pos+size)
        return ret

    def seek(self, delta, postype=os.SEEK_SET):
        if postype == os.SEEK_END:
            self.pos = len(self.data) + delta
        elif postype == os.SEEK_CUR:
            self.pos = self.pos + delta
        else:
            self.pos = delta
        if self.pos >= len(self.data):
            self.pos = len(self.data)-1
        if self.pos < 0:
            self.pos = 0

    def tell(self):
        return self.pos
