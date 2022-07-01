import math
import geo
import logging
from heapq import heappush, heappop
import rprofile

class Node:
    def __init__(self, id, lat, lon):
        self.id = id
        self.point = geo.Point.fromlatlon(lat, lon)

    def __repr__(self):
        return 'Node #{0} at {1}'.format(self.id, self.point)

    @classmethod
    def distance(cls, node1, node2):
        return geo.Point.distance(node1.point, node2.point)

class Way:
    def __init__(self, id):
        self.id = id
        self.nodes = []
        self.tags = {}

    def length(self):
        dist = 0
        for i in range (0, len(self.nodes)-1):
            dist += Node.distance(self.nodes[i], self.nodes[i+1])
        return dist

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
        self.tags = {}

    @classmethod
    def fromway(cls, start, finish, cost):
        edge = cls()
        edge.start = start
        edge.finish = finish
        edge.cost = cost
        return edge

class Neighbor:
    def __init__(self, node, edge):
        self.node = node
        self.edge = edge

class Routing:
    ''' Routing graph with nodes, edges and neighbours 
        neighbors - mapping between nodes and array of Neighbor objects '''
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.neighbors = {}

class Route:
    def __init__(self):
        self.nodes = []

class Router:
    def __init__(self, rdata, start, finish):
        self.rdata = rdata
        self.start = start
        self.finish = finish
        self.profile = rprofile.Profile()

    def route(self):
        logging.debug('Routing from %s(%s) to %s(%s), distance %s', self.start.id, self.start.point, self.finish.id, self.finish.point, Node.distance(self.start, self.finish))
        if self.start == self.finish:
            route = Route()
            route.nodes.extend([self.start, self.finish])
            return route
        self.frontier = []
        heappush(self.frontier, RoutingNode(self.start, None, 0) )
        self.visited = { self.start : 0 }
        while len(self.frontier) > 0:
            top = heappop(self.frontier)
#            logging.debug('Processing node %s, cost %s, dist %s, frontier %s', top.node.id, top.cost, distance(top.node, self.finish), len(self.frontier))
            for n in self.rdata.neighbors[top.node]:
                if n.node == self.finish:
                    self.route = self.makeroute(top)
                    return self.route
                cost = top.cost + self.cost(n.edge) + Node.distance(n.node, self.finish)
#                logging.debug('  checking node %s, cost %s', n.node.id, cost)
                if n.node not in self.visited or cost < self.visited[n.node]:
                    heappush(self.frontier, RoutingNode(n.node, top, cost))
                    self.visited[n.node] = cost
        return None

    def cost(self, edge):
        return edge.cost

    def makeroute(self, way):
        route = Route()
        while way != None:
            route.nodes.insert(0, way.node)
            way = way.source
        route.nodes.append(self.finish)
        return route

class RoutingNode:
    ''' Node for routing. It contain node reference, source reference and total cost (route and heuristic) '''
    def __init__(self, node, source, cost):
        self.node = node
        self.source = source
        self.cost = cost

    def __lt__(self, other):
        return self.cost < other.cost

    def __eq__(self, other):
        if other == None:
            return False
        return self.cost == other.cost

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
        jedge = { 'start':edge.start.id, 'finish':edge.finish.id, 'cost':edge.cost, 'tags':{} }
        for k, v in edge.tags.items():
            jedge['tags'][k] = v
        return jedge

    @classmethod
    def loadedge(cls, nodes, neighbors, jedge):
        edge = Edge.fromway(nodes[jedge['start']], nodes[jedge['finish']], jedge['cost'])
        for k, v in jedge['tags'].items():
            edge.tags[k] = v
        cls.addneighbor(neighbors, edge.start, edge.finish, edge)
        cls.addneighbor(neighbors, edge.finish, edge.start, edge)
        return edge

    @classmethod
    def addneighbor(cls, neighbors, node, neighbor, edge):
        if node not in neighbors:
            neighbors[node] = []
        neighbors[node].append( Neighbor(neighbor, edge) )
