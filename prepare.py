#!/usr/bin/python3

import sys
import os
import json
import math
sys.path.insert(1, os.path.abspath('../geo'))
import routing

def makeedge(start, finish, way):
    return routing.Edge.fromway(start, finish, routing.distance(start, finish))

def prepare(mapdata):
    rdata = routing.Routing()
    rdata.nodes = mapdata.nodes
    for way in mapdata.ways:
        for i in range(0, len(way.nodes)-1):
            rdata.edges.append( makeedge(way.nodes[i], way.nodes[i+1], way) )
    print('Total ', len(rdata.nodes), 'nodes', len(rdata.edges), 'edges')
    return rdata

def main(fways, frouting):
    print('loading')
    with open(fways) as jfile:
        mapdata = routing.MapJson.load(json.load(jfile))
    print('preparing')
    rdata = prepare(mapdata)
    print('Storing')
    with open(frouting, 'w') as jfile:
        json.dump( routing.RoutingJson.save(rdata), jfile, indent = 2 )

if __name__ == '__main__':
    main('mm.ways', 'mm.routing')