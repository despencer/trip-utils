from dbmeta import DbMeta

class DbTrack:
    def __init__(self):
        DbMeta.init(self)

    @classmethod
    def getbyname(cls, db, name):
        return DbMeta.getby(db, cls, "name = ?", name)

    @classmethod
    def create(cls, db, name, hash):
        track = cls()
        track.id = db.genid()
        track.name = name
        track.hash = hash
        DbMeta.insert(db, track)
        return track

class DbTrackPoint:
    def __init__(self):
        DbMeta.init(self)

    @classmethod
    def cleartrack(cls, db, track):
        db.execute("DELETE FROM tracks_point WHERE track = ?", (track,) )

    @classmethod
    def create(cls, db, track, pos, otime, ctime, lat, lon, alt):
#        print(pos, otime, ctime, lat, lon, alt)
        point = cls()
        point.track = track
        point.pos = pos
        point.otime = int(otime.timestamp()) if otime != None else None
        point.ctime = int(ctime.timestamp())
        point.lat = lat
        point.lon = lon
        point.alt = alt
        DbMeta.insert(db, point)
        return point

def init(db):
    db.deploypacket('tracks',1,
        [ "CREATE TABLE tracks_track (id INTEGER NOT NULL, name TEXT NOT NULL, hash BLOB NOT NULL, PRIMARY KEY(id), UNIQUE(name))",
        '''CREATE TABLE tracks_point (track INTEGER NOT NULL, pos INTEGER NOT NULL, otime INTEGER NULL, ctime INTEGER NOT NULL,
              lat REAL NOT NULL, lon REAL NOT NULL, alt REAL NULL, PRIMARY KEY (track, pos), FOREIGN KEY (track) REFERENCES tracks_track(id))'''])
    DbMeta.set(DbTrack, 'tracks_track', ['id', 'name', 'hash'])
    DbMeta.set(DbTrackPoint, 'tracks_point', ['track','pos', 'otime', 'ctime', 'lat', 'lon', 'alt'] )
