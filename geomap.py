import json
import geo
import tiles

class Map:
    def __init__(self):
        pass

    def makedraw(self, projection = geo.simplemercator):
        draw = MapDraw(self)
        center = tiles.totilepoint( projection (self.center), self.zoom )
        left = center.x - int(self.size.width/2)
        top = center.y - int(self.size.height/2)
        draw.bounds = geo.Bounds( left, top, left+self.size.width, top+self.size.height)
        return draw

    @classmethod
    def load(cls, filename):
        with open(filename) as jfile:
            jmap = json.load(jfile)
            return cls.fromjson(jmap)

    @classmethod
    def fromjson(cls, jmap):
        mapspec = Map()
        mapspec.name = jmap['name']
        mapspec.zoom = jmap['zoom']
        mapspec.center = geo.Point.fromjson(jmap['center'])
        mapspec.size = geo.Size.fromjson(jmap['size'])
        return mapspec

class MapDraw:
    def __init__(self, mapdesc):
        self.mapdesc = mapdesc