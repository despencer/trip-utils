import math

class Point:
    ''' values are in radians (2*PI x 2*PI) right-top square '''
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    @classmethod
    def fromjson(cls, jpoint):
        return Point( cls.torad(cls.coordfromjson(jpoint['lat'])), cls.torad(cls.coordfromjson(jpoint['lon'])) )

    @classmethod
    def torad(cls, deg):
        ''' degrees to radians transformation '''
        return deg * math.pi / 180

    @classmethod
    def coordfromjson(cls, jcoord):
        if 'N' in jcoord:
            return jcoord['N'] + jcoord['min']/60
        elif 'S' in jcoord:
            return -(jcoord['S'] + jcoord['min']/60)
        elif 'W' in jcoord:
            return -(jcoord['W'] + jcoord['min']/60)
        elif 'E' in jcoord:
            return -(jcoord['E'] + jcoord['min']/60)
        return 0

class MapPoint:
    ''' point in the projection '''
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Size:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @classmethod
    def fromjson(cls, jsize):
        return Size(jsize['width'], jsize['height'])

class Bounds:
    ''' right and bottom points are exclusive '''
    def __init__(self, l, t, r, b):
        self.left = l
        self.top = t
        self.right = r
        self.bottom = b

    def __repr__(self):
        return "{0}x{1} - {2}x{3}".format(self.left, self.top, self.right, self.bottom)

def simplemercator(loc):
    ''' This is a Mercator projection. It transforms lat-lon to (2*PI x 2*PI) right-top square '''
    sin = math.sin(loc.lat)
    return MapPoint( loc.lon, 0.5 * math.log( (1+sin) / (1-sin) ) )
