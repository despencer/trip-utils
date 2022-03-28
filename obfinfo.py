#!/usr/bin/python3

import logging
from obfreader import ObfReader
from pbreader import ProtobufReader

obstr = { 1 : { 'format':'d' } }

def main(fname):
    with open(fname, 'rb') as obfile:
        reader = ObfReader(obfile)
        reader.readall()

def main2(fname):
    with open(fname, 'rb') as obfile:
        reader = ProtobufReader(obfile, obstr)
        reader.read()

if __name__ == '__main__':
    logging.basicConfig(filename='obinfo.log', filemode='w', level=logging.DEBUG)
    main2('/mnt/mobihome/maps/Russia_central-federal-district_asia_2.obf')

