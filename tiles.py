import math
import geo

tilesize = 256

class TileCache:
    def __init__(self):
        pass


def totilepoint(mappoint, zoom):
    x = mappoint.x + math.pi
    y = math.pi - mappoint.y
    numtiles = (1 << (zoom-1) ) * tilesize
    x = int( x * numtiles / (math.pi * 2) )
    y = int( y * numtiles / (math.pi * 2) )
    return geo.MapPoint(x, y)