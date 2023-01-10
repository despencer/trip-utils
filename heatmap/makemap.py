#!/usr/bin/python3
import argparse
import logging
import skia
import itertools
import sys
import os
sys.path.insert(1, os.path.abspath('../geo'))
sys.path.insert(1, os.path.abspath('../tilecache'))
sys.path.insert(1, os.path.abspath('../tracks'))
sys.path.insert(1, os.path.abspath('../../pydma'))
import mapdraw
import tiles
import geomap
import trackdb

def drawheat(view, mapspec, section):
    proj = view.projection()
    cell = geomap.MapPoint( int(mapspec.size.x / mapspec.granularity), int(mapspec.size.y / mapspec.granularity) )
    origin = mapspec.gettilebounds(proj).corners()[0]
    with trackdb.Db(section) as db:
        for x, y in itertools.product( range(0, mapspec.size.x, cell.x), range(0, mapspec.size.y, cell.y) ):
            cellbounds = geomap.MapBounds.fromltrb(origin.x+x, origin.y+y, origin.x+x+cell.x, origin.y+y+cell.y)
            cellgeo = cellbounds.mapcorners( lambda x:geomap.fromtilepoint(x, mapspec.zoom) ).togeo(proj)
            print(cellbounds, cellgeo, len(trackdb.DbTrackPoint.getbybounds(db, cellgeo)))

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
    mapspec = mapdraw.Map.load(mapfile)
    with tiles.TileCache(mapspec.storage) as cache:
        view = cache.openview(mapspec.provider)
        proj = view.projection()
        bounds = mapspec.gettilebounds(proj)
        print('Map', bounds)
        view.updatetiles(bounds, mapspec.zoom)
        canvas = mapspec.opencanvas()
#        drawbase(view, canvas, bounds, mapspec.zoom)
        drawheat(view, mapspec, 'walking')
        mapspec.store(canvas)

if __name__ == '__main__':
    logging.basicConfig(filename='makemap.log', filemode='w', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Making heatmap')
    parser.add_argument('map', help='map file')
    args = parser.parse_args()
    make(args.map)
