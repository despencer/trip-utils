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
    def create(cls, db, name, hash, tdate):
        track = cls()
        track.id = db.genid()
        track.name = name
        track.hash = hash
        track.tdate = int(tdate.timestamp())
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

    @classmethod
    def getdatebybounds(cls, db, bounds):
      return db.execute('''SELECT DISTINCT t.id, t.tdate FROM tracks_point p, tracks_track t
             WHERE p.lat >= ? AND p.lat < ? AND p.lon >= ? AND p.lon < ? AND p.track = t.id''', (bounds.bottom.value, bounds.top.value, bounds.left.value, bounds.right.value) )

def open(section):
    dbpath = os.path.expanduser(trackdir)
    if not os.path.exists(dbpath):
         os.makedirs(dbpath)
    dbpath = os.path.join(dbpath, section + ".tracks")
    return dbmeta.Db(dbpath, initdb)

def initdb(db):
    db.deploypacket('tracks',1,
            [ "CREATE TABLE tracks_track (id INTEGER NOT NULL, name TEXT NOT NULL, hash BLOB NOT NULL, tdate INTEGER NOT NULL, PRIMARY KEY(id), UNIQUE(name))",
            '''CREATE TABLE tracks_point (track INTEGER NOT NULL, pos INTEGER NOT NULL, otime INTEGER NULL, ctime INTEGER NOT NULL,
                  lat REAL NOT NULL, lon REAL NOT NULL, alt REAL NULL, PRIMARY KEY (track, pos), FOREIGN KEY (track) REFERENCES tracks_track(id))'''])
    dbmeta.DbMeta.set(DbTrack, 'tracks_track', ['id', 'name', 'hash', 'tdate'])
    dbmeta.DbMeta.set(DbTrackPoint, 'tracks_point', ['track','pos', 'otime', 'ctime', 'lat', 'lon', 'alt'] )

