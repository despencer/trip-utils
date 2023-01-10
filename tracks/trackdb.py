import os
import dbmeta

trackdir = "~/.tiles"

class DbTrack:
    def __init__(self):
        dbmeta.DbMeta.init(self)

    @classmethod
    def getbyname(cls, db, name):
        return dbmeta.DbMeta.getby(db, cls, "name = ?", name)

    @classmethod
    def create(cls, db, name, hash):
        track = cls()
        track.id = db.genid()
        track.name = name
        track.hash = hash
        dbmeta.DbMeta.insert(db, track)
        return track

class DbTrackPoint:
    def __init__(self):
        dbmeta.DbMeta.init(self)

    @classmethod
    def cleartrack(cls, db, track):
        db.execute("DELETE FROM tracks_point WHERE track = ?", (track,) )

    @classmethod
    def create(cls, db, track, pos, otime, ctime, lat, lon, alt):
        point = cls()
        point.track = track
        point.pos = pos
        point.otime = int(otime.timestamp()) if otime != None else None
        point.ctime = int(ctime.timestamp())
        point.lat = lat
        point.lon = lon
        point.alt = alt
        dbmeta.DbMeta.insert(db, point)
        return point

    @classmethod
    def getbybounds(cls, db, bounds):
        return dbmeta.DbMeta.getlist(db, cls, "lat >= ? AND lat < ? AND lon >= ? AND lon < ?", bounds.bottom.value, bounds.top.value, bounds.left.value, bounds.right.value)

class Db:
    def __init__(self, section):
        dbpath = os.path.expanduser(trackdir)
        if not os.path.exists(dbpath):
            os.makedirs(dbpath)
        self.dbpath = os.path.join(dbpath, section + ".tracks")

    def init(self):
        self.db.deploypacket('tracks',1,
            [ "CREATE TABLE tracks_track (id INTEGER NOT NULL, name TEXT NOT NULL, hash BLOB NOT NULL, PRIMARY KEY(id), UNIQUE(name))",
            '''CREATE TABLE tracks_point (track INTEGER NOT NULL, pos INTEGER NOT NULL, otime INTEGER NULL, ctime INTEGER NOT NULL,
                  lat REAL NOT NULL, lon REAL NOT NULL, alt REAL NULL, PRIMARY KEY (track, pos), FOREIGN KEY (track) REFERENCES tracks_track(id))'''])
        dbmeta.DbMeta.set(DbTrack, 'tracks_track', ['id', 'name', 'hash'])
        dbmeta.DbMeta.set(DbTrackPoint, 'tracks_point', ['track','pos', 'otime', 'ctime', 'lat', 'lon', 'alt'] )

    def open(self):
        self.db = dbmeta.Db(self.dbpath)
        self.db.open()
        self.init()
        self.run = self.db.run()

    def finish(self, success=True):
        self.run.finish(success)
        self.db.close()
        self.run = None
        self.db = None

    def __enter__(self):
        self.open()
        return self.run

    def __exit__(self, extype, exvalue, extrace):
        self.finish(extype == None)

