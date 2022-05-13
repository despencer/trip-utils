import geo

class Node:
    def __init__(self, id, lat, lon):
        self.id = id
        self.point = geo.Point.fromlatlon(lat, lon)

    def __repr__(self):
        return 'Node #{0} at {1}'.format(self.id, self.point)

class Way:
    def __init__(self, id):
        self.id = id
        self.nodes = []

class BeyondNode:
    def __init__(self, id):
        self.id = id
        self.ways = []

class Map:
    def __init__(self):
        self.nodes = {}
        self.ways = []

    @classmethod
    def fromdata(cls, nodes, ways):
        map = Map()
        map.nodes = nodes
        map.ways = ways
        return map

class MapJson:
    @classmethod
    def load(cls, jmap):
        rd = Map()
        cls.loadnodes(rd, jmap['nodes'])
        cls.loadways(rd, jmap['ways'])
        return rd

    @classmethod
    def save(cls, mapdata):
        return { 'nodes':cls.savenodes(mapdata), 'ways':cls.saveways(mapdata) }

    @classmethod
    def loadnodes(cls, md, jnodes):
        for jn in jnodes:
            node = cls.loadnode(jn)
            md[node.id] = node

    @classmethod
    def loadways(cls, md, jways):
        for jw in jways:
            md.ways.append(cls.loadway(md.nodes, jw))

    @classmethod
    def savenodes(cls, md):
        jnodes = []
        for n in md.nodes:
            jnodes.append(cls.savenode(n))
        return jnodes

    @classmethod
    def saveways(cls, md):
        jways = []
        for w in md.ways:
            jways.append(cls.saveway(w))
        return jways

    @classmethod
    def loadnode(cls, jnode):
        return Node(jnode['id'], jnode['lat'], jnode['lon'])

    @classmethod
    def loadway(cls, nodes, jway):
        way = Way(jway['id'])
        for jn in jway['nodes']):
            way.nodes.append(nodes[jn])
        return way

    @classmethod
    def savenode(cls, node):
        return { 'id':node.id, 'lat':node.point.lat.value, 'lon':node.point.lon.value }

    @classmethod
    def saveway(cls, way):
        jway = { 'id':way.id, 'nodes':[] }
        for n in way.nodes:
            jway['nodes'].append(n.id)
        return jway

