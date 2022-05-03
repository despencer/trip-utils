#!/usr/bin/python3

import sys
import os
import logging
sys.path.insert(1, os.path.abspath('../geo'))
import pbfdata

def main(fname):
    with open(fname, 'rb') as pbfile:
        pbfmap = pbfdata.readpbf(pbfile)
        print(pbfmap.prettyprint(''))

if __name__ == '__main__':
    logging.basicConfig(filename='pbinfo.log', filemode='w', level=logging.INFO)
    main('/mnt/mobihome/maps/central-fed-district-latest.osm.pbf')
