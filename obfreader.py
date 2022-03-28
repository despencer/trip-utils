import pbreader

import logging
from collections import defaultdict
from pbreader import RawReader

class ObfReader:
    def __init__(self, obf):
        self.pbraw = RawReader.fromfile(obf)
        self.mapindice = []

    def readall(self):
        self.readheader()
        self.readmaps()

    def readheader(self):
        self.pbraw.readtags( defaultdict( lambda: self.pbraw.read_bywiretype,
            { 1:self.pbraw.read_varintvalue, 18:self.pbraw.read_varintvalue,      # version dateCreated
            6: self.read_mapsection,
            32: self.pbraw.read_varintvalue } ) )     # version confirm

    def read_mapsection(self, rawtag):
        amount, size = rawtag.reader.read_fixed(4, 'big')
        logging.debug('map section at %X with size %X', rawtag.pos+size, amount)
        self.mapindice.append( rawtag.section(size, amount) )
        return (size+amount , False)

    def readmaps(self):
        for ms in self.mapindice:
            logging.debug('reading map: %s', ms)
            reader = RawReader.fromsection(ms)
            reader.readtags( defaultdict( lambda: self.pbraw.read_bywiretype ) )
