#!/usr/bin/python3

from datetime import datetime, timedelta
import sys
import os
import json
import math
import logging
import argparse
from datetime import datetime, timezone
sys.path.insert(1, os.path.abspath('../geo'))
import geo
import routing
import rprofile

def loadtrack(nodes, fname):
    with open(fname, encoding='cp1251') as tfile:
        lines = tfile.readlines()
    route = routing.Route()
    for i in range(6, len(lines)):
        fields = lines[i].split(',')
        lat = float(fields[0])
        lon = float(fields[1])
        p = geo.Point.fromlatlon(lat, lon)
        node = locatenode(nodes, p)
        route.nodes.append(node)
    return route

def savetrack(fname, route):
    print('saving to', fname)
    ts = datetime.now().astimezone(tz=timezone.utc)
    fts = ts - datetime(1899, 12, 30, tzinfo=timezone.utc)
    sts = '{0:13.7f}, {1}, {2}'.format( fts.days+(fts.seconds/86400),  ts.strftime('%d-%b-%y'), ts.strftime('%H:%M:%S'))
    with open(fname, 'w') as rfile:
        rfile.write('OziExplorer Track Point File Version 2.1\r\nWGS 84\r\nAltitude is in Feet\r\nReserved 3\r\n0,2,255,A route,0,0,2,255\r\n')
        rfile.write('{0}\r\n'.format(len(route.nodes)))
        for i,n in enumerate(route.nodes):
            rfile.write('{0:11.6f},{1:11.6f},{2}, -777.0,{3}\r\n'.format(n.point.lat.value, n.point.lon.value, 1 if i==0 else 0, sts))

def locatenode(nodes, point):
    bounds = point.boundslatlon(0.5/60, 0.5/60)
    candidate = None
    distance = None
    for node in nodes.values():
        if bounds.isinside(node.point):
            if candidate == None or geo.Point.distance(node.point, point) < distance:
                candidate = node
                distance = geo.Point.distance(node.point, point)
    return candidate

def main(frouting, fwaypoints, froute):
    fprofile = 'default.profile'
    print('loading profile', fprofile)
    profile = rprofile.load(fprofile)
    tstart = datetime.now()
    print('loading', frouting)
    with open(frouting) as jfile:
        rdata = routing.RoutingJson.load(json.load(jfile))
    tlocating = datetime.now()
    print('locating waypoints', fwaypoints)
    waypoints = loadtrack(rdata.nodes, fwaypoints)
    if len(waypoints.nodes) <= 1:
        print('waypoints should be at least 2')
        return
    trouting = datetime.now()
    print('routing')
    route = routing.Route()
    for i in range(0, len(waypoints.nodes)-1):
        print('Routing ', i, 'segment of', len(waypoints.nodes)-1)
        router = routing.Router(rdata, waypoints.nodes[i], waypoints.nodes[i+1])
        router.profile = profile
        part = router.route()
        if part == None:
            print('sorry, no route')
            return
        if len(route.nodes) == 0:
            route.nodes.extend(part.nodes)
        else:
            route.nodes.extend(part.nodes[1:])
    tfinish = datetime.now()
    savetrack(froute, route)
    print('loading', tlocating-tstart, 'locating', trouting-tlocating,'routing', tfinish-trouting)

if __name__ == '__main__':
    logging.basicConfig(filename='route.log', filemode='w', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Routes via waypoints')
    parser.add_argument('routing', help='a routing file')
    parser.add_argument('waypoints', help='a waypoint file')
    parser.add_argument('target', help='a target file')
    args = parser.parse_args()
    main(args.routing, args.waypoints, args.target)