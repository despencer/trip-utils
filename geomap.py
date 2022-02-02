import json
import geo

class Map:
    def __init__(self):
        pass

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

