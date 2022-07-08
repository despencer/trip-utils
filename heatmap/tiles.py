import os
import json
import math
import geo

tilesize = 256

class TileCache:
    def __init__(self):
        pass

    @classmethod
    def init(cls, filename):
        with open(filename) as jfile:
            jcache = json.load(jfile)
        indexfile = os.path.expanduser(jcache['cache']['index'])
        print("Index file", indexfile)
        dir, file = os.path.split(indexfile)
        print(dir, file)

class View:
    def __init__(self):
        self.bounds = geo.Bounds(0, 0, 1, 1)
        self.zoom = 1

def totilepoint(mappoint, zoom):
    x = mappoint.x + math.pi
    y = math.pi - mappoint.y
    numtiles = (1 << (zoom-1) ) * tilesize
    x = int( x * numtiles / (math.pi * 2) )
    y = int( y * numtiles / (math.pi * 2) )
    return geo.MapPoint(x, y)