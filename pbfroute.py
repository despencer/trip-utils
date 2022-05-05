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
        for i, blob in enumerate(osmfile.blobs):
            block = blob.blob.readcontents()
            for j in range(0, len(block.strings.strings)):
                print(j, block.strings.strings[j])
            if i > 100:
                break

if __name__ == '__main__':
    logging.basicConfig(filename='pbroute.log', filemode='w', level=logging.INFO)
    main('/mnt/mobihome/maps/central-fed-district-latest.osm.pbf')
