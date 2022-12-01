import os
import json
import math
import geo
import dbmeta
import providers
import datetime
import logging

cachedir = "~/.tiles"

class TileProvider:
    def __init__(self):
        dbmeta.DbMeta.init(TileProvider, self)

    @classmethod
    def create(cls, db, name):
        provider = cls()
        provider.id = db.genid()
        provider.name = name
        return dbmeta.DbMeta.insert(db, cls, provider)

class TileVersion:
    def __init__(self):
        dbmeta.DbMeta.init(TileVersion, self)

    @classmethod
    def create(cls, db, provider, no, parameter):
        version = cls()
        version.id = db.genid()
        version.provider = provider
        version.version_no = no
        version.version_parameter = parameter
        return dbmeta.DbMeta.insert(db, cls, version)

    @classmethod
    def getlast(cls, db, provider):
        return dbmeta.DbMeta.selectone(db, cls,
           ''' SELECT v.id, v.provider, v.version_no, v.version_parameter FROM tile_version v, tile_provider p
                WHERE v.provider = p.id AND p.name = ? ORDER BY v.version_no DESC''', provider)

class TileView:
    def __init__(self, cache, version, provider):
        self.cache = cache
        self.version = version
        self.provider = provider
        logging.info('TileView version %s/%s created', version.version_no, version.version_parameter)

class TileCache:
    def __init__(self, cachename):
        self.cachename = cachename
        self.providers = { 'osm' : providers.OsmProvider() }

    def open(self):
        tpath = os.path.expanduser(cachedir)
        if not os.path.exists(tpath):
            os.makedirs(tpath)
        indexfile = os.path.join(tpath, self.cachename + ".tindex")
        self.db = dbmeta.Db(indexfile)
        self.db.open()
        self.dbrun = self.db.run()
        self.initdb()

    def close(self):
        self.dbrun.finish()
        self.db.close()
        self.dbrun = None
        self.db = None

    def openview(self, provider):
        return TileView(self, TileVersion.getlast(self.dbrun, provider), self.providers[provider])

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, extype, exvalue, extrace):
        self.close()

    def initdb(self):
        fresh = self.db.deploypacket('gis.tiles',1,
          [ "CREATE TABLE tile_provider (id INTEGER NOT NULL, name TEXT NOT NULL, PRIMARY KEY(id), UNIQUE(name))",
            "CREATE TABLE tile_version (id INTEGER NOT NULL, provider INTEGER NOT NULL, version_no INTEGER NOT NULL, version_parameter TEXT NOT NULL, PRIMARY KEY (id), UNIQUE (provider, version_no), FOREIGN KEY (provider) REFERENCES tile_provider (id))",
            '''CREATE TABLE tile_tile (version INTEGER NOT NULL, ZOOM INTEGER NOT NULL, x INTEGER NOT NULL, y INTEGER NOT NULL, download INTEGER NOT NULL,
                 offset INTEGER NOT NULL, SIZE INTEGER NOT NULL, PRIMARY KEY (version, zoom, x, y), FOREIGN KEY (version) REFERENCES tile_version (id))'''])
        dbmeta.DbMeta.set(TileProvider, 'tile_provider', ['id', 'name'])
        dbmeta.DbMeta.set(TileVersion, 'tile_version', ['id', 'provider', 'version_no', 'version_parameter'])
        if fresh:
            osm = TileProvider.create(self.dbrun, 'osm')
            TileVersion.create(self.dbrun, osm.id, 1, datetime.datetime.now().strftime('%Y%m%d') )
