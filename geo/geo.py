from geopy import distance

def findmulti(string, values):
    for c in values:
        if string.find(c) >= 0:
            return string.find(c)
    return -1

class Coordinate:
    def __init__(self):
        self.axis = 'lat'
        self.value = 0

    def __repr__(self):
        if self.axis == 'lat':
            prefix = 'N' if self.value >= 0 else 'S'
        else:
            prefix = 'E' if self.value >= 0 else 'W'
        return "{0}{1:.3f}".format(prefix, abs(self.value))

    @classmethod
    def parse(cls, strvalue):
        c = Coordinate()
        strvalue = strvalue.strip()
        if strvalue[0] in ['N', 'S', 'E', 'W']:
            c.value = float(strvalue[1:])
            c.setaxis(strvalue[0])
        else:
            ind = findmulti(strvalue, ['N', 'S', 'E', 'W'])
            c.value = int(strvalue[:ind]) + float(strvalue[ind+1:])/60
            c.setaxis(strvalue[ind])
        return c

    def setaxis(self, nsew):
        if nsew in ('N','S'):
            if nsew == 'S':
                self.value = -self.value
        else:
            self.axis = 'lon'
            if nsew == 'W':
                self.value = -self.value

class Point:
    def __init__(self):
        self.lat = Coordinate()
        self.lon = Coordinate()
        self.lon.axis = 'lon'

    def __repr__(self):
        return "{0} @ {1}".format(self.lat, self.lon)

    @classmethod
    def fromlatlon(cls, lat, lon):
        ret = cls()
        ret.lat.value = lat
        ret.lon.value = lon
        return ret

    @classmethod
    def parse(cls, strvalue):
        points = strvalue.split('@')
        return cls.fromlatlon(Coordinate.parse(points[0]).value, Coordinate.parse(points[1]).value)

    def boundslatlon(self, lat, lon):
        """ returns bounds around the point with the lat and lon margins"""
        bounds = Rectangle()
        bounds.left.value = self.lon.value - lon
        bounds.top.value = self.lat.value + lat
        bounds.right.value = self.lon.value + lon
        bounds.bottom.value = self.lat.value - lat
        return bounds

    @classmethod
    def distance(cls, pt1, pt2):
        return distance.distance( (pt1.lat.value, pt1.lon.value), (pt2.lat.value, pt2.lon.value) ).m

class Rectangle:
    def __init__(self):
        self.left = Coordinate()
        self.top = Coordinate()
        self.right = Coordinate()
        self.bottom = Coordinate()
        self.left.axis = 'lon'
        self.right.axis = 'lon'

    def __repr__(self):
        return "{0} @ {1} - {2} @ {3}".format(self.top, self.left, self.bottom, self.right)

    @classmethod
    def fromltrb(self, left, top, right, bottom):
        r = Rectangle()
        r.left.value = left
        r.top.value = top
        r.right.value = right
        r.bottom.value = bottom
        return r

    def corners(self):
        lt = Point()
        rb = Point()
        lt.lon.value = self.left.value
        lt.lat.value = self.top.value
        rb.lon.value = self.right.value
        rb.lat.value = self.bottom.value
        return [ lt, rb ]

    @classmethod
    def parse(cls, strvalue):
        r = Rectangle()
        points = strvalue.split('-')
        lt = Point.parse(points[0])
        rb = Point.parse(points[1])
        r.left.value = lt.lon.value
        r.top.value = lt.lat.value
        r.right.value = rb.lon.value
        r.bottom.value = rb.lat.value
        return r

    def isinside(self, point):
        return self.left.value <= point.lon.value and point.lon.value <= self.right.value and self.bottom.value <= point.lat.value and point.lat.value <= self.top.value

    def isintersects(self, arect):
        return ((self.left.value <= arect.left.value and arect.left.value <= self.right.value) or
                (self.left.value <= arect.right.value and arect.right.value <= self.right.value) or
                (arect.left.value <= self.left.value and self.right.value <= arect.right.value)) and ((self.bottom.value <= arect.top.value and arect.top.value <= self.top.value) or
                (self.bottom.value <= arect.bottom.value and arect.bottom.value <= self.top.value) or
                (arect.bottom.value <= self.bottom.value and self.top.value <= arect.top.value))
