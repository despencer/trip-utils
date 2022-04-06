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
        self.boxes = []