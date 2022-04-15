#!/usr/bin/python3

import sys
import os
import logging
sys.path.insert(1, os.path.abspath('../geo'))
import obfdata
import geo

def main(fname, pfrom):
    print('From {0}'.format(pfrom))
    with open(fname, 'rb') as obfile:
        obfmap = obfdata.readobf(obfile)
        nodes = obfmap.locatenodes(22, pfrom)
        for n in nodes:
            print(n.bounds, len(n.block.strings.table))

if __name__ == '__main__':
    mosmm = geo.Point.fromlatlon(55 + (38.444/60), 37 + (31.804/60) )
    logging.basicConfig(filename='obroute.log', filemode='w', level=logging.INFO)
    main('/mnt/mobihome/maps/Russia_central-federal-district_asia_2.obf', mosmm)

