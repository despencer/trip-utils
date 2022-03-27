#!/usr/bin/python3

import logging
from obfreader import ObfReader

def main(fname):
    with open(fname, 'rb') as obfile:
        reader = ObfReader(obfile)
        reader.readheader()

if __name__ == '__main__':
    logging.basicConfig(filename='obinfo.log', filemode='w', level=logging.DEBUG)
    main('/mnt/mobihome/maps/Russia_central-federal-district_asia_2.obf')

