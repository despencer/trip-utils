import json
import geo
import tiles

class Map:
    def __init__(self):
        pass

    def makeview(self, projection = geo.simplemercator):
        view = tiles.View()
        center = tiles.totilepoint( projection (self.center), self.zoom )
        left = center.x - int(self.size.width/2)
        top = center.y - int(self.size.height/2)
        view.bounds = geo.Bounds( left, top, left+self.size.width, top+self.size.height)
        view.zoom = self.zoom
        return view

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

class View:
    def __init__(self):
        pass