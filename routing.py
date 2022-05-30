import math
import geo

def pdistance(start, finish):
    lat = finish.lat.value - start.lat.value
    lon = finish.lon.value - start.lon.value
    return math.sqrt( (lat*lat) + (lon*lon) )

def distance(start, finish):
    return pdistance(start.point, finish.point)

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
        self.tags = {}

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

class Edge:
    def __init__(self):
        self.start = None
        self.finish = None
        self.cost = None

    @classmethod
    def fromway(cls, start, finish, cost):
        edge = cls()
        edge.start = start
        edge.finish = finish
        edge.cost = cost
        return edge

class Neighbor:
    def __init__(self, node, cost):
        self.node = node
        self.cost = cost

class Routing:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.neighbors = {}

class Route:
    def __init__(self):
        self.nodes = []

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
            md.nodes[node.id] = node

    @classmethod
    def loadways(cls, md, jways):
        for jw in jways:
            md.ways.append(cls.loadway(md.nodes, jw))

    @classmethod
    def savenodes(cls, md):
        jnodes = []
        for n in md.nodes.values():
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
        for jn in jway['nodes']:
            way.nodes.append(nodes[jn])
        for k, v in jway['tags'].items():
            way.tags[k] = v
        return way

    @classmethod
    def savenode(cls, node):
        return { 'id':node.id, 'lat':node.point.lat.value, 'lon':node.point.lon.value }

    @classmethod
    def saveway(cls, way):
        jway = { 'id':way.id, 'nodes':[], 'tags':{} }
        for n in way.nodes:
            jway['nodes'].append(n.id)
        for k, v in way.tags.items():
            jway['tags'][k] = v
        return jway

class RoutingJson:
    @classmethod
    def save(cls, routing):
        return { 'nodes':MapJson.savenodes(routing), 'edges':cls.saveedges(routing) }

    @classmethod
    def load(cls, jrouting):
        routing = Routing()
        MapJson.loadnodes(routing, jrouting['nodes'])
        cls.loadedges(routing, jrouting['edges'])
        return routing

    @classmethod
    def saveedges(cls, routing):
        jedges = []
        for e in routing.edges:
            jedges.append(cls.saveedge(e))
        return jedges

    @classmethod
    def loadedges(cls, routing, jedges):
        for je in jedges:
            routing.edges.append(cls.loadedge(routing.nodes, routing.neighbors, je))

    @classmethod
    def saveedge(cls, edge):
        return { 'start':edge.start.id, 'finish':edge.finish.id, 'cost':edge.cost }

    @classmethod
    def loadedge(cls, nodes, neighbors, jedge):
        edge = Edge.fromway(nodes[jedge['start']], nodes[jedge['finish']], jedge['cost'])
        cls.addneighbor(neighbors, edge.start, edge.finish, edge.cost)
        cls.addneighbor(neighbors, edge.finish, edge.start, edge.cost)
        return edge

    @classmethod
    def addneighbor(cls, neighbors, node, neighbor, cost):
        if node not in neighbors:
            neighbors[node] = []
        neighbors[node].append( Neighbor(neighbor, cost) )
