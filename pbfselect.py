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

class Way:
    def __init__(self, id):
        self.id = id
        self.nodes = []

class Selector:
    def __init__(self, osmfile, bounds):
        self.osmfile = osmfile
        self.bounds = bounds
        self.ibounds = geo.Rectangle.fromltrb(round(bounds.left.value*10000000), round(bounds.top.value*10000000), round(bounds.right.value*10000000), round(bounds.bottom.value*10000000))
        self.wayblocks = None

    def locatenodes(self):
        print('Selecting nodes for bounds', self.bounds)
        nodes = {}
        self.wayblocks = []
        indy = Indicator()
        for i in range(0, len(self.osmfile.blobs)):
            blob = self.osmfile.blobs[i]
            if indy.ready():
                print('Selecting nodes', i,'/',len(self.osmfile.blobs), 'nodes found', len(nodes))
            block = blob.blob.readcontents()
            for p in block.primitives:
                if len(p.ways) > 0 and (i not in self.wayblocks):
                    self.wayblocks.append(i)
                if p.densenodes != None:
                    for j in range(0, len(p.densenodes.ids)):
                        if self.ibounds.left.value <= p.densenodes.lons[j] and p.densenodes.lons[j] <= self.ibounds.right.value and self.ibounds.bottom.value <= p.densenodes.lats[j] and p.densenodes.lats[j] <= self.ibounds.top.value:
                            node = Node(p.densenodes.ids[j], p.densenodes.lats[j]/10000000, p.densenodes.lons[j]/10000000)
                            nodes[node.id] = node
        return nodes

    def locateways(self, locnodes):
        nodes = {}
        ways = []
        beyond = []
        indy = Indicator()
        for i, iblock in enumerate(self.wayblocks):
            if indy.ready():
                print('Selecting ways', i,'/',len(self.wayblocks))
            block = self.osmfile.blobs[iblock].blob.readcontents()
            for p in block.primitives:
                for w in p.ways:
                    for waynode in w.refs:
                        if waynode in locnodes:
                            way = Way(w.id)
                            ways.append(w)
                            break
        return (ways, nodes, beyond)

    def locate(self):
        locnodes = self.locatenodes()
        ways, nodes, beyond = self.locateways(locnodes)
        print('Total nodes', len(nodes), 'ways', len(ways), 'beyond', len(beyond))

def main(fname):
    with open(fname, 'rb') as pbfile:
        osmfile = pbfdata.readpbf(pbfile)
        selector = Selector(osmfile, geo.Rectangle.fromltrb(37 + (31.704/60), 55 + (38.544/60), 37 + (31.904/60), 55 + (38.344/60) ))
        selector.locate()

if __name__ == '__main__':
    logging.basicConfig(filename='pbroute.log', filemode='w', level=logging.INFO)
    main('/mnt/mobihome/maps/central-fed-district-latest.osm.pbf')
