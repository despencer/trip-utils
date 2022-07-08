#!/usr/bin/python3

import sys
import os
import logging
sys.path.insert(1, os.path.abspath('../geo'))
import obfdata

def printnodes(indent, node):
    if len(node.children) == 0:
        return
    print('{0}Node at {1}, {2} children, mapblock={3}'.format(indent, node.bounds, len(node.children), 'Yes' if node.block != None else 'No'))
    for c in node.children:
        printnodes(indent+'    ', c)

def main(fname):
    with open(fname, 'rb') as obfile:
        obfmap = obfdata.readobf(obfile)
        print('Map version {0}'.format(obfmap.version))
        for s in obfmap.sections:
            print('Section {0}'.format(s.name))
            for l in s.maplevels:
                print('Map level {0}-{1} at {2}'.format(l.minzoom, l.maxzoom, l.bounds))
                printnodes('    ', l.node)

if __name__ == '__main__':
    logging.basicConfig(filename='obinfo.log', filemode='w', level=logging.INFO)
    main('/mnt/mobihome/maps/Russia_central-federal-district_asia_2.obf')

