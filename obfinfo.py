#!/usr/bin/python3

import logging
from datetime import datetime, timedelta
from obfreader import ObfReader
from pbreader import ProtobufReader

def unixtime(x):
    return datetime(1970,1,1)+timedelta(milliseconds=x)

obstr = { 1 : { 'format':'d' }, 18:{'format':'', 'factory':unixtime},
    6:{ 'children':{     # map_section
        2:{'format':'', 'factory':ProtobufReader.readutf8},
        5:{'format':'', 'default':'MapLevel', 'children':{
            1:{'format':'', 'name':'max'}, 2:{'format':'', 'name':'min'} }}   },
        'print':4 } }      # map_section

def main(fname):
    with open(fname, 'rb') as obfile:
        reader = ObfReader(obfile)
        reader.readall()

def main2(fname):
    with open(fname, 'rb') as obfile:
        reader = ProtobufReader(obfile, obstr)
        reader.read()

if __name__ == '__main__':
    logging.basicConfig(filename='obinfo.log', filemode='w', level=logging.INFO)
    main2('/mnt/mobihome/maps/Russia_central-federal-district_asia_2.obf')

