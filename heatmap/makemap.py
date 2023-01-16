#!/usr/bin/python3
import argparse
import logging
import skia
import itertools
import sys
import os
from datetime import datetime, timezone
import math
sys.path.insert(1, os.path.abspath('../geo'))
sys.path.insert(1, os.path.abspath('../tilecache'))
sys.path.insert(1, os.path.abspath('../tracks'))
sys.path.insert(1, os.path.abspath('../../pydma'))
import mapdraw
import tiles
import geomap
import trackdb

class Cell:
    def __init__(self):
        pass

def drawheat(view, mapspec, section):
    proj = view.projection()
    cellsize = geomap.MapPoint( int(mapspec.size.x / mapspec.heatmap.granularity), int(mapspec.size.y / mapspec.heatmap.granularity) )
    origin = mapspec.gettilebounds(proj).corners()[0]
    now = int(datetime.now(timezone.utc).timestamp())
    cells = []
    maxvalue = 0
    with trackdb.open(section) as db:
        for x, y in itertools.product( range(0, mapspec.size.x, cellsize.x), range(0, mapspec.size.y, cellsize.y) ):
            cell = Cell()
            cell.bounds = geomap.MapBounds.fromltrb(origin.x+x, origin.y+y, origin.x+x+cellsize.x, origin.y+y+cellsize.y)
            cell.geo = cell.bounds.mapcorners( lambda x:geomap.fromtilepoint(x, mapspec.zoom) ).togeo(proj)
            cell.value = 0.0
            for _, tdate in trackdb.DbTrackPoint.getdatebybounds(db, cell.geo):
                cell.value += math.exp( (now-tdate) / mapspec.heatmap.fading)
#                print(datetime.fromtimestamp(tdate), now-tdate, int(datetime.now(timezone.utc).timestamp())-now, value )
            cells.append(cell)
            if maxvalue < cell.value:
                maxvalue = cell.value
    canvas = mapspec.opencanvas()
    canvas.canvas.clear(0)
    for cell in cells:
        rect = skia.Rect( cell.bounds.left-origin.x, cell.bounds.top-origin.y, cell.bounds.right-origin.x, cell.bounds.bottom-origin.y)
        color = int(cell.value * 255 / maxvalue)
        canvas.canvas.drawRect(rect, skia.Paint(Color= (color<<24) | (0xFF0000) ) )
    return canvas

def drawbase(view, canvas, bounds, zoom):
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
    mapspec = mapdraw.HeatMap.load(mapfile)
    with tiles.TileCache(mapspec.storage) as cache:
        view = cache.openview(mapspec.provider)
        proj = view.projection()
        bounds = mapspec.gettilebounds(proj)
        print('Map', bounds)
        view.updatetiles(bounds, mapspec.zoom)
        canvas = mapspec.opencanvas()
        drawbase(view, canvas, bounds, mapspec.zoom)
        heatcanvas = drawheat(view, mapspec, 'walking')
        canvas.canvas.drawImage(heatcanvas.surface.makeImageSnapshot(), 0, 0)
        mapspec.store(canvas)

if __name__ == '__main__':
    logging.basicConfig(filename='makemap.log', filemode='w', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Making heatmap')
    parser.add_argument('map', help='map file')
    args = parser.parse_args()
    make(args.map)
