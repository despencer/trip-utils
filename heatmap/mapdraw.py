import json
import geo
import geomap
import skia

class Canvas:
    def __init__(self, width, height):
        self.surface = skia.Surface(width, height)
        self.canvas = self.surface.getCanvas()

class Map:
    def __init__(self):
        pass

    @classmethod
    def load(cls, filename):
        with open(filename) as jfile:
            jmap = json.load(jfile)
            return cls.fromjson(jmap)

    @classmethod
    def fromjson(cls, jfile):
        jmap = jfile['map']
        mapspec = Map()
        mapspec.center = geo.Point.parse(jmap['center'])
        mapspec.size = geomap.MapPoint.parse(jmap['size'])
        mapspec.storage = jmap['source']['storage']
        mapspec.provider = jmap['source']['provider']
        mapspec.zoom = int(jmap['source']['zoom'])
        mapspec.target = jmap['target']
        mapspec.granularity = 10
        return mapspec

    def gettilebounds(self, proj):
        lt = geomap.totilepoint(proj.toprojection(self.center), self.zoom)
        lt.x -= int(self.size.x / 2)
        lt.y -= int(self.size.y / 2)
        return geomap.MapBounds.fromltrb(lt.x, lt.y, lt.x+self.size.x-1, lt.y+self.size.y-1)

    def opencanvas(self):
        return Canvas(self.size.x, self.size.y)

    def store(self, canvas):
        image = canvas.surface.makeImageSnapshot()
        image.save(self.target, skia.kPNG)
