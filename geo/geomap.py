import math

tilesize = 256
tilepower = 8

class MapPoint:
    ''' point in the projection '''
    def __init__(self, x, y):
        self.x = x
        self.y = y

class MapBounds:
    ''' right and bottom points are exclusive '''
    def __init__(self):
        self.left = 0
        self.top = 0
        self.right = 0
        self.bottom = 0

    @classmethod
    def fromltrb(cls, left, top, right, bottom):
        m = cls()
        m.left = left
        m.top = top
        m.right = right
        m.bottom = bottom

    @classmethod
    def frombounds(cls, bounds, projection):
        return cls.fromcorners( *list(map(projection, bounds.corners())) )

    def corners(self):
        lt = MapPoint(self.left, self.top)
        rb = MapPoint(self.right, self.bottom)
        return [ lt, rb ]

    def mapcorners(self, func):
        return MapBounds.fromcorners( *list(map( func, self.corners() )) )

    @classmethod
    def fromcorners(cls, lt, rb):
        m = cls()
        m.left = lt.x
        m.top = lt.y
        m.right = rb.x
        m.bottom = rb.y
        return m

    def __repr__(self):
        return "{0}x{1} - {2}x{3}".format(self.left, self.top, self.right, self.bottom)


def simplemercator(point):
    ''' This is a Mercator projection. It transforms lat-lon to (2*PI x 2*PI) right-top square '''
    lat = point.lat.value * math.pi / 180
    lon = point.lon.value * math.pi / 180
    sin = math.sin(lat)
    return MapPoint( lon, 0.5 * math.log( (1+sin) / (1-sin) ) )

def totilepoint(mappoint, zoom):
    x = mappoint.x + math.pi
    y = math.pi - mappoint.y
    numtiles = (1 << (zoom-1) ) * tilesize
    x = int( x * numtiles / (math.pi * 2) )
    y = int( y * numtiles / (math.pi * 2) )
    return MapPoint(x, y)

def gettileno(mappoint):
    return MapPoint( mappoint.x >> tilepower, mappoint.y >> tilepower)
