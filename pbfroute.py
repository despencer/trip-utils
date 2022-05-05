#!/usr/bin/python3

import sys
import os
import logging
sys.path.insert(1, os.path.abspath('../geo'))
import pbfdata
from reader import Indicator

def main(fname):
    with open(fname, 'rb') as pbfile:
        osmfile = pbfdata.readpbf(pbfile)
        for i in [3, 12001, 12331]:
            blob = osmfile.blobs[i]
            block = blob.blob.readcontents()
            for p in block.primitives:
                if p.densenodes != None:
                    print(p.densenodes.keyvals)

if __name__ == '__main__':
    logging.basicConfig(filename='pbroute.log', filemode='w', level=logging.INFO)
    main('/mnt/mobihome/maps/central-fed-district-latest.osm.pbf')
