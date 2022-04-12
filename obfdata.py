import math
import geo

# longitude from integer to degrees
def lonitod(x):
    return (x * 360.0 / (1024.0 * (1<<21))) - 180.0

def latitod(y):
    sign = -1 if y < 0 else 1
    arg = math.pi * ( 1.0 - ( y / (512.0 * (1<<21))  ) )
    return math.atan(sign * math.sinh(arg)) * 180.0 / math.pi

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
        self.ibounds = geo.Rectangle()
        self._bounds = None
        self._node = None
        self._nodereader = None

    @property
    def node(self):
        if self._nodereader != None:
            self._nodereader()
            self._nodereader = None
            self._node.adjustbounds(self.ibounds)
        return self._node

    @property
    def bounds(self):
        if self._bounds == None:
            self._bounds = geo.Rectangle()
            self._bounds.left.value = lonitod(self.ibounds.left.value)
            self._bounds.top.value = latitod(self.ibounds.top.value)
            self._bounds.right.value = lonitod(self.ibounds.right.value)
            self._bounds.bottom.value = latitod(self.ibounds.bottom.value)
        return self._bounds

class MapNode:
    def __init__(self):
        self.ibounds = geo.Rectangle()
        self.bounds = geo.Rectangle()
        self.children = []
        self._children = []

    def adjustbounds(self, parent):
        self.ibounds.left.value += parent.left.value
        self.ibounds.top.value += parent.top.value
        self.ibounds.right.value += parent.right.value
        self.ibounds.bottom.value += parent.bottom.value
        self.bounds.left.value = lonitod(self.ibounds.left.value)
        self.bounds.top.value = latitod(self.ibounds.top.value)
        self.bounds.right.value = lonitod(self.ibounds.right.value)
        self.bounds.bottom.value = latitod(self.ibounds.bottom.value)
