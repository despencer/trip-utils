#!/usr/bin/python3

import sys
import os
import logging
sys.path.insert(1, os.path.abspath('../geo'))
import obfdata
import geo

def constructbounds(pfrom):
   return pfrom.boundslatlon(0.5/60, 0.5/60)

def main(fname, pfrom):
    print('From {0} ({1})'.format(pfrom, constructbounds(pfrom)))
    with open(fname, 'rb') as obfile:
        obfmap = obfdata.readobf(obfile)
        objects = obfmap.locateobjects(22, constructbounds(pfrom))
        for o in objects.values():
            print('    Object', o.id, o.coordinates)

if __name__ == '__main__':
    mosmm = geo.Point.fromlatlon(55 + (38.444/60), 37 + (31.804/60) )
    logging.basicConfig(filename='obroute.log', filemode='w', level=logging.INFO)
    main('/mnt/mobihome/maps/Russia_central-federal-district_asia_2.obf', mosmm)

