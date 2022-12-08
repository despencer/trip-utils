import json
import geo
import geomap

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
        return mapspec
