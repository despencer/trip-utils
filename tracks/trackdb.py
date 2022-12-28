import dbmeta

class DbTrack:
    def __init__(self):
        dbmeta.DbMeta.init(DbTrack, self)

    @classmethod
    def getbyname(cls, db, name):
        return dbmeta.DbMeta.getby(db, cls, "name = ?", name)

    @classmethod
    def create(cls, db, name, hash):
        track = cls()
        track.id = db.genid()
        track.name = name
        track.hash = hash
        dbmeta.DbMeta.insert(db, cls, track)
        return track

def init(db):
    db.deploypacket('tracks',1,
        [ "CREATE TABLE tracks_track (id INTEGER NOT NULL, name TEXT NOT NULL, hash BLOB NOT NULL, PRIMARY KEY(id), UNIQUE(name))",
        '''CREATE TABLE tracks_point (track INTEGER NOT NULL, pos INTEGER NOT NULL, otime INTEGER NOT NULL, ctime INTEGER NOT NULL,
              lat REAL NOT NULL, lon REAL NOT NULL, alt REAL NOT NULL, PRIMARY KEY (track, pos), FOREIGN KEY (track) REFERENCES tracks_track(id))'''])
    dbmeta.DbMeta.set(DbTrack, 'tracks_track', ['id', 'name', 'hash'])
