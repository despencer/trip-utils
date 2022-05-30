#!/usr/bin/python3

import sys
import os
import json
import math
from datetime import datetime, timezone
sys.path.insert(1, os.path.abspath('../geo'))
import geo
import routing

mosmm = geo.Point.fromlatlon(55 + (38.444/60), 37 + (31.804/60) )
target = geo.Point.fromlatlon(55 + (38.792/60), 37 + (31.763/60) )

def savetrack(fname, route):
    ts = datetime.now().astimezone(tz=timezone.utc)
    fts = ts - datetime(1899, 12, 30, tzinfo=timezone.utc)
    sts = '{0:13.7f}, {1}, {2}'.format( fts.days+(fts.seconds/86400),  ts.strftime('%d-%b-%y'), ts.strftime('%H:%M:%S'))
    with open(fname, 'w') as rfile:
        rfile.write('OziExplorer Track Point File Version 2.1\r\nWGS 84\r\nAltitude is in Feet\r\nReserved 3\r\n0,2,255,A route,0,0,2,255\r\n')
        rfile.write('{0}\r\n'.format(len(route.nodes)))
        for i,n in enumerate(route.nodes):
            rfile.write('{0:11.6f},{1:11.6f},{2}, -777.0,{3}\r\n'.format(n.point.lat.value, n.point.lon.value, 1 if i==0 else 0, sts))

def locatenode(nodes, point):
    candidate = None
    distance = None
    for node in nodes.values():
        if candidate == None or routing.pdistance(node.point, point) < distance:
            candidate = node
            distance = routing.pdistance(node.point, point)
    return candidate

def main(frouting, froute, pstart, pfinish):
    print('loading')
    with open(frouting) as jfile:
        rdata = routing.RoutingJson.load(json.load(jfile))
    print('Locating start and finish')
    start = locatenode(rdata.nodes, pstart)
    finish = locatenode(rdata.nodes, pfinish)
    route = routing.Route()
    route.nodes.append(start)
    route.nodes.append(finish)
    savetrack(froute, route)

if __name__ == '__main__':
    main('mm-small.routing', '/mnt/mobihome/temp/trial.plt', mosmm, target)