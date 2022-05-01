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

    def boundslatlon(self, lat, lon):
        """ returns bounds around the point with the lat and lon margins"""
        bounds = Rectangle()
        bounds.left.value = self.lon.value - lon
        bounds.top.value = self.lat.value + lat
        bounds.right.value = self.lon.value + lon
        bounds.bottom.value = self.lat.value - lat
        return bounds

class Rectangle:
    def __init__(self):
        self.left = Coordinate()
        self.top = Coordinate()
        self.right = Coordinate()
        self.bottom = Coordinate()
        self.left.axis = 'lon'
        self.right.axis = 'lon'

    def __repr__(self):
        return "{0} @ {1} - {2} @ {3}".format(self.left, self.top, self.right, self.bottom)

    def isinside(self, point):
        return self.left.value <= point.lon.value and point.lon.value <= self.right.value and self.bottom.value <= point.lat.value and point.lat.value <= self.top.value

    def isintersects(self, arect):
        return ((self.left.value <= arect.left.value and arect.left.value <= self.right.value) or
                (self.left.value <= arect.right.value and arect.right.value <= self.right.value) or
                (arect.left.value <= self.left.value and self.right.value <= arect.right.value)) and ((self.bottom.value <= arect.top.value and arect.top.value <= self.top.value) or
                (self.bottom.value <= arect.bottom.value and arect.bottom.value <= self.top.value) or
                (arect.bottom.value <= self.bottom.value and self.top.value <= arect.top.value))
