#!/usr/bin/python3

import sys
import os
import logging
sys.path.insert(1, os.path.abspath('../geo'))
import pbfdata
from reader import Indicator
import geo

class Node:
    def __init__(self, id, lat, lon):
        self.id = id
        self.point = geo.Point.fromlatlon(lat, lon)

    def __repr__(self):
        return 'Node #{0} at {1}'.format(self.id, self.point)

def locatenodes(osmfile, bounds):
    ibounds = geo.Rectangle.fromltrb(round(bounds.left.value*10000000), round(bounds.top.value*10000000), round(bounds.right.value*10000000), round(bounds.bottom.value*10000000))
    nodes = []
    print('Bounds', bounds)
    indy = Indicator()
    for i, blob in enumerate(osmfile.blobs):
        if indy.ready():
            print(i,'/',len(osmfile.blobs), 'nodes found', len(nodes))
        block = blob.blob.readcontents()
        for p in block.primitives:
            if p.densenodes != None:
                for j in range(0, len(p.densenodes.ids)):
                    if ibounds.left.value <= p.densenodes.lons[j] and p.densenodes.lons[j] <= ibounds.right.value and ibounds.bottom.value <= p.densenodes.lats[j] and p.densenodes.lats[j] <= ibounds.top.value:
                        node = Node(p.densenodes.ids[j], p.densenodes.lats[j]/10000000, p.densenodes.lons[j]/10000000)
                        nodes.append(node)
    for n in nodes:
        print(n)

def main(fname):
    with open(fname, 'rb') as pbfile:
        osmfile = pbfdata.readpbf(pbfile)
        locatenodes(osmfile, geo.Rectangle.fromltrb(37 + (31.704/60), 55 + (38.544/60), 37 + (31.904/60), 55 + (38.344/60) ))

if __name__ == '__main__':
    logging.basicConfig(filename='pbroute.log', filemode='w', level=logging.INFO)
    main('/mnt/mobihome/maps/central-fed-district-latest.osm.pbf')
