#!/usr/bin/python3

import sys
import os
import json
import math
import argparse
sys.path.insert(1, os.path.abspath('../geo'))
import routing
from reader import Indicator

def makeedge(start, finish, way):
    edge = routing.Edge.fromway(start, finish, way.length())
    edge.tags = way.tags
    return edge

def prepare(mapdata):
    rdata = routing.Routing()
    rdata.nodes = mapdata.nodes
    indy = Indicator()
    for i, way in enumerate(mapdata.ways):
        if indy.ready():
            print('Processing ways', i,'/',len(mapdata.ways))
        for i in range(0, len(way.nodes)-1):
            rdata.edges.append( makeedge(way.nodes[i], way.nodes[i+1], way) )
    print('Total ', len(rdata.nodes), 'nodes', len(rdata.edges), 'edges')
    return rdata

def main(fways, frouting):
    print('loading from', fways)
    with open(fways) as jfile:
        mapdata = routing.MapJson.load(json.load(jfile))
    print('preparing')
    rdata = prepare(mapdata)
    print('Storing to', frouting)
    with open(frouting, 'w') as jfile:
        json.dump( routing.RoutingJson.save(rdata), jfile, indent = 2 )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepares data for routing')
    parser.add_argument('ways', help='a ways file')
    parser.add_argument('routing', help='a routing file')
    args = parser.parse_args()
    main(args.ways, args.routing)