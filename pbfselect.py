#!/usr/bin/python3

import sys
import os
import logging
import json
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

class BeyondNode:
    def __init__(self, id):
        self.id = id
        self.ways = []

class Selector:
    def __init__(self, osmfile, bounds):
        self.osmfile = osmfile
        self.bounds = bounds
        self.ibounds = geo.Rectangle.fromltrb(round(bounds.left.value*10000000), round(bounds.top.value*10000000), round(bounds.right.value*10000000), round(bounds.bottom.value*10000000))
        self.wayblocks = None
        self.nodeblock = None

    def locatenodes(self):
        print('Selecting nodes for bounds', self.bounds)
        nodes = {}
        self.wayblocks = []
        self.nodeblocks = []
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
                    self.nodeblocks.append(i)
                    for j in range(0, len(p.densenodes.ids)):
                        if self.ibounds.left.value <= p.densenodes.lons[j] and p.densenodes.lons[j] <= self.ibounds.right.value and self.ibounds.bottom.value <= p.densenodes.lats[j] and p.densenodes.lats[j] <= self.ibounds.top.value:
                            node = Node(p.densenodes.ids[j], p.densenodes.lats[j]/10000000, p.densenodes.lons[j]/10000000)
                            nodes[node.id] = node
        return nodes

    def addwaynodes(self, way, refs, nodes, locnodes, beyond):
        for refnode in refs:
            if refnode in nodes:
                way.nodes.append(nodes[refnode])
            else:
                if refnode in locnodes:
                    nodes[refnode] = locnodes[refnode]
                    way.nodes.append(nodes[refnode])
                else:
                    if refnode not in beyond:
                        beyond[refnode] = BeyondNode(refnode)
                    beyond[refnode].ways.append( (way, len(way.nodes)) )
                    way.nodes.append( Node(0, 0, 0) )

    def locateways(self, locnodes):
        nodes = {}
        ways = []
        beyond = {}
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
                            ways.append(way)
                            self.addwaynodes(way, w.refs, nodes, locnodes, beyond)
                            break
        return (ways, nodes, beyond)

    def updateways(self, ways, beyondref, node):
        for way, ipoint in beyondref.ways:
            way.nodes[ipoint] = node

    def getbeyondnodes(self, ways, nodes, beyond):
        indy = Indicator()
        for i, iblock in enumerate(self.nodeblocks):
            if indy.ready():
                print('Getting beyond nodes', i,'/',len(self.nodeblocks))
            block = self.osmfile.blobs[iblock].blob.readcontents()
            for p in block.primitives:
                for j in range(0, len(p.densenodes.ids)):
                    if p.densenodes.ids[j] in beyond:
                        node = Node(p.densenodes.ids[j], p.densenodes.lats[j]/10000000, p.densenodes.lons[j]/10000000)
                        nodes[node.id] = node
                        self.updateways(ways, beyond[node.id], node)

    def locate(self):
        locnodes = self.locatenodes()
        ways, nodes, beyond = self.locateways(locnodes)
        self.getbeyondnodes(ways, nodes, beyond)
        return (ways, nodes)

def store(tname, ways):
    print('Storing')
    jways = []
    for w in ways:
        jw = { 'id':w.id, 'points':[] }
        for n in w.nodes:
            jpoint = { 'lat':n.point.lat.value, 'lon':n.point.lon.value }
            jw['points'].append(jpoint)
        jways.append(jw)
    with open(tname, 'w') as jfile:
        json.dump( {'ways':jways }, jfile, indent = 2 )

def main(fname, tname):
    with open(fname, 'rb') as pbfile:
        osmfile = pbfdata.readpbf(pbfile)
        selector = Selector(osmfile, geo.Rectangle.fromltrb(37 + (31.704/60), 55 + (38.544/60), 37 + (31.904/60), 55 + (38.344/60) ))
        ways, nodes = selector.locate()
    store(tname, ways)

if __name__ == '__main__':
    logging.basicConfig(filename='pbroute.log', filemode='w', level=logging.INFO)
    main('/mnt/mobihome/maps/central-fed-district-latest.osm.pbf','mm.ways')
