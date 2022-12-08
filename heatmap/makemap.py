#!/usr/bin/python3
import argparse
import logging
import sys
import os
sys.path.insert(1, os.path.abspath('../geo'))
sys.path.insert(1, os.path.abspath('../tilecache'))
sys.path.insert(1, os.path.abspath('../../pydma'))
import mapdraw
import tiles
import geomap

def make(mapfile):
    mapspec = mapdraw.Map.load(mapfile)
    with tiles.TileCache(mapspec.storage) as cache:
        view = cache.openview(mapspec.provider)
        proj = view.projection()
        lt = geomap.totilepoint(proj.toprojection(mapspec.center), mapspec.zoom)
        lt.x -= int(mapspec.size.x / 2)
        lt.y -= int(mapspec.size.y / 2)
        bounds = geomap.MapBounds.fromltrb(lt.x, lt.y, lt.x+mapspec.size.x, lt.y+mapspec.size.y)
        print(bounds)

if __name__ == '__main__':
    logging.basicConfig(filename='makemap.log', filemode='w', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Making heatmap')
    parser.add_argument('map', help='map file')
    args = parser.parse_args()
    make(args.map)
