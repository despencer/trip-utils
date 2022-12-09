#!/usr/bin/python3
import argparse
import logging
import skia
import sys
import os
sys.path.insert(1, os.path.abspath('../geo'))
sys.path.insert(1, os.path.abspath('../tilecache'))
sys.path.insert(1, os.path.abspath('../../pydma'))
import mapdraw
import tiles
import geomap

def drawmap(view, canvas, bounds, zoom):
    corner = bounds.corners()[0]
    basetileno = geomap.gettileno(corner)
    baseoffset = geomap.gettileorigin(basetileno)
    offset = geomap.MapPoint(baseoffset.x, baseoffset.y)
    while offset.x <= bounds.right:
        offset.y = baseoffset.y
        while offset.y <= bounds.bottom:
            tileno = geomap.gettileno(offset)
            tile = view.gettile(tileno.x, tileno.y, zoom)
            canvas.canvas.drawImage(skia.Image.MakeFromEncoded(tile.data), offset.x-corner.x, offset.y-corner.y)
            offset.y += geomap.tilesize
        offset.x += geomap.tilesize

def make(mapfile):
    mapspec = mapdraw.Map.load(mapfile)
    with tiles.TileCache(mapspec.storage) as cache:
        view = cache.openview(mapspec.provider)
        proj = view.projection()
        bounds = mapspec.gettilebounds(proj)
        print('Map', bounds)
        view.updatetiles(bounds, mapspec.zoom)
        canvas = mapspec.opencanvas()
        drawmap(view, canvas, bounds, mapspec.zoom)
        mapspec.store(canvas)

if __name__ == '__main__':
    logging.basicConfig(filename='makemap.log', filemode='w', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Making heatmap')
    parser.add_argument('map', help='map file')
    args = parser.parse_args()
    make(args.map)
