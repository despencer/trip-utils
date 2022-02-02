class Point:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    @classmethod
    def fromjson(cls, jpoint):
        return Point( cls.coordfromjson(jpoint['lat']), cls.coordfromjson(jpoint['lon']) )

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

class Size:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @classmethod
    def fromjson(cls, jsize):
        return Size(jsize['width'], jsize['height'])