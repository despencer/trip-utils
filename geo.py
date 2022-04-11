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
