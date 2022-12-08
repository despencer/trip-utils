#!/usr/bin/python3
import argparse
import logging
import sys
import os
sys.path.insert(1, os.path.abspath('../geo'))
sys.path.insert(1, os.path.abspath('../../pydma'))
import geo
import geomap
import tiles

def update(storage, bounds, level):
    print('Checking storage ', args.storage)
    with tiles.TileCache(args.storage) as cache:
        print('Updating ', bounds, ' at ', level)
        view = cache.openview('osm')
        tilebounds = geomap.MapBounds.frombounds(bounds, view.projection().toprojection).mapcorners(lambda p: geomap.totilepoint(p,level))
        view.updatetiles(tilebounds, level)

if __name__ == '__main__':
    logging.basicConfig(filename='update.log', filemode='w', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Tile database updates')
    parser.add_argument('storage', help='tile storage')
    parser.add_argument('bounds', help='bounds to update')
    parser.add_argument('level', help='bounds to update')
    args = parser.parse_args()
    update(args.storage, geo.Rectangle.parse(args.bounds), int(args.level))
