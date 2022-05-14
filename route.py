#!/usr/bin/python3

import sys
import os
import json
import math
sys.path.insert(1, os.path.abspath('../geo'))
import geo
import routing

mosmm = geo.Point.fromlatlon(55 + (38.444/60), 37 + (31.804/60) )
target = geo.Point.fromlatlon(55 + (38.792/60), 37 + (31.763/60) )

def locatenode(nodes, point):
    candidate = None
    distance = None
    for node in nodes.values():
        if candidate == None or routing.pdistance(node.point, point) < distance:
            candidate = node
            distance = routing.pdistance(node.point, point)
    return candidate

def main(frouting, pstart, pfinish):
    print('loading')
    with open(frouting) as jfile:
        rdata = routing.RoutingJson.load(json.load(jfile))
    print('Locating start and finish')
    start = locatenode(rdata.nodes, pstart)
    finish = locatenode(rdata.nodes, pfinish)
    print(start, finish)

if __name__ == '__main__':
    main('mm-small.routing', mosmm, target)