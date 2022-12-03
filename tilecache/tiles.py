import os
import json
import math
import geo
import dbmeta
import providers
import datetime
import logging
import requests
from urllib.parse import urlparse

cachedir = "~/.tiles"

class Loader:
    def __init__(self, url):
        self.url = url
        self.data = None

    def load(self):
        host = urlparse(self.url).hostname
        headers = { 'Host':host, 'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language':'en-US,en;q=0.5' }
        response = requests.request('GET', self.url, headers=headers)
        logging.info('Status code %s', response.status_code)
        if response.status_code == 200:
            self.data = response.content

    def ok(self):
        return self.data != None

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
class Tile:
    def __init__(self):
        dbmeta.DbMeta.init(Tile, self)

    @classmethod
    def getbypos(cls, db, provider, x, y, zoom):
        return dbmeta.DbMeta.selectone(db, cls,
            ''' SELECT t.version, t.zoom, t.x, t.y, t.download, t.offset, t.size FROM tile_tile t, tile_version v
                 WHERE t.version = v.id AND t.zoom = ? AND t.x = ? AND t.y = ? AND v.provider = ? ORDER BY v.version_no DESC''',
            zoom, x, y, provider)


class TileView:
    def __init__(self, cache, version, provider):
        self.cache = cache
        self.version = version
        self.provider = provider
        logging.info('TileView version %s/%s created', version.version_no, version.version_parameter)

    def check(self, x, y, zoom):
        tile = Tile.getbypos(self.cache.dbrun, self.version.provider, x, y, zoom)
        if tile == None or tile.version != self.version.id:
            url = self.provider.geturl(x, y, zoom, self.version.version_parameter)
            logging.info('Tile %s@%s at %s is old, requesting %s', x, y, zoom, url)
            loader = Loader(url)
            loader.load()
            if loader.ok():
                self.store(loader.data, x, y, zoom)

    def store(self, data, x, y, zoom):
        newtile = Tile()
        newtile.version = self.version.id
        newtile.x = x
        newtile.y = y
        newtile.zoom = zoom
        newtile.download = dbmeta.DbMeta.now()
        self.cache.tiles.seek(0, os.SEEK_END)
        newtile.offset = self.cache.tiles.tell()
        newtile.size = len(data)
        self.cache.tiles.write(data)
        dbmeta.DbMeta.insert(self.cache.dbrun, Tile, newtile)
        self.cache.dbrun.finish()
        logging.info('Tile %s@%s at %s written at %s size %s', newtile.x, newtile.y, newtile.zoom, newtile.offset, newtile.size)

class TileCache:
    def __init__(self, cachename):
        self.cachename = cachename
        self.providers = { 'osm' : providers.OsmProvider() }

    def open(self):
        tpath = os.path.expanduser(cachedir)
        if not os.path.exists(tpath):
            os.makedirs(tpath)
        indexfile = os.path.join(tpath, self.cachename + ".tindex")
        imagefile = os.path.join(tpath, self.cachename + ".tiles")
        self.db = dbmeta.Db(indexfile)
        self.db.open()
        self.dbrun = self.db.run()
        self.initdb()
        self.tiles = open(imagefile, 'ab')

    def close(self):
        self.dbrun.finish()
        self.db.close()
        self.dbrun = None
        self.db = None
        self.tiles.close()
        self.tiles = None

    def openview(self, provider):
        return TileView(self, TileVersion.getlast(self.dbrun, provider), self.providers[provider])

    def addversion(self, provider, parameter):
        version = TileVersion.getlast(self.dbrun, provider)
        TileVersion.create(self.dbrun, version.provider, version.version_no+1, parameter )
        self.dbrun.finish()

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
                 offset INTEGER NOT NULL, size INTEGER NOT NULL, PRIMARY KEY (version, zoom, x, y), FOREIGN KEY (version) REFERENCES tile_version (id))'''])
        dbmeta.DbMeta.set(TileProvider, 'tile_provider', ['id', 'name'])
        dbmeta.DbMeta.set(TileVersion, 'tile_version', ['id', 'provider', 'version_no', 'version_parameter'])
        dbmeta.DbMeta.set(Tile, 'tile_tile', ['version', 'zoom', 'x', 'y', 'download', 'offset', 'size'])
        if fresh:
            osm = TileProvider.create(self.dbrun, 'osm')
            TileVersion.create(self.dbrun, osm.id, 1, datetime.datetime.now().strftime('%Y%m%d') )
