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
