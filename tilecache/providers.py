import geomap

class OsmProvider:
    def __init__(self):
        self.projection = geomap.SimpleMercator()

    def geturl(self, x, y, zoom, version):
        return "http://tile.openstreetmap.org/{0}/{1}/{2}.png".format(zoom-1, x, y)

