import geo

class Map:
    def __init__(self):
        self.version = None
        self.sections = []

class Section:
    def __init__(self):
        self.name = None
        self.maplevels = []

class MapLevel:
    def __init__(self):
        self.minzoom = None
        self.maxzoom = None
        self.bounds = geo.Rectangle()
        self._node = None
        self._nodereader = None

    @property
    def node(self):
        if self._nodereader != None:
            self._nodereader()
            self._nodereader = None
        return self._node

class MapNode:
    def __init__(self):
        self.bounds = geo.Rectangle()
        self.children = []
        self._children = []