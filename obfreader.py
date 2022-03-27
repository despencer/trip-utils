import pbreader

import logging
from collections import defaultdict
from pbreader import RawReader

class ObfReader:
    def __init__(self, obf):
        self.pbraw = RawReader(obf)

    def readheader(self):
        self.pbraw.readtags( defaultdict( lambda: self.pbraw.read_bywiretype,
            { 1:self.pbraw.read_varintvalue, 18:self.pbraw.read_varintvalue,      # version dateCreated
            6: lambda x: self.readsection('mapIndex', x),
            7: lambda x: self.readsection('addressIndex', x),
            4: lambda x: self.readsection('transportIndex', x),
            9: lambda x: self.readsection('routingIndex', x),
            8: lambda x: self.readsection('poiIndex', x),
            32: self.pbraw.read_varintvalue } ) )     # version confirm

    def readsection(self, name, rawtag):
        amount, size = rawtag.reader.read_fixed(4, 'big')
        logging.debug('Section %s at %s with size %s', name, rawtag.pos, amount)
        return (size+amount , False)
