import os
import json
import math
import geo
import dbmeta

cachedir = "~/.tiles"

class TileCache:
    def __init__(self):
        pass

    @classmethod
    def init(cls, cachename):
        tpath = os.path.expanduser(cachedir)
        if not os.path.exists(tpath):
            os.makedirs(tpath)
        indexfile = os.path.join(tpath, cachename + ".tindex")
        with dbmeta.Db(indexfile) as db:
            cls.initdb(db)

    @classmethod
    def initdb(cls, db):
        db.deploypacket('gis.tiles',1,
          [ "CREATE TABLE tile_provider (id INTEGER NOT NULL, name TEXT NOT NULL, PRIMARY KEY(id), UNIQUE(name))",
            "CREATE TABLE tile_version (id INTEGER NOT NULL, provider INTEGER NOT NULL, version_no INTEGER NOT NULL, version_parameter TEXT NOT NULL, PRIMARY KEY (id), UNIQUE (provider, version_no), FOREIGN KEY (provider) REFERENCES tile_provider (id))",
            '''CREATE TABLE tile_tile (version INTEGER NOT NULL, ZOOM INTEGER NOT NULL, x INTEGER NOT NULL, y INTEGER NOT NULL, download INTEGER NOT NULL,
                 offset INTEGER NOT NULL, SIZE INTEGER NOT NULL, PRIMARY KEY (version, zoom, x, y))'''])


class View:
    def __init__(self):
        self.bounds = geo.Bounds(0, 0, 1, 1)
        self.zoom = 1

