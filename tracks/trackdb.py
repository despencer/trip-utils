import dbmeta

def init(db):
    db.deploypacket('tracks',1,
        [ "CREATE TABLE tracks_track (id INTEGER NOT NULL, name TEXT NOT NULL, hash INTEGER NOT NULL, PRIMARY KEY(id), UNIQUE(name))",
        '''CREATE TABLE tracks_point (track INTEGER NOT NULL, pos INTEGER NOT NULL, otime INTEGER NOT NULL, ctime INTEGER NOT NULL,
              lat REAL NOT NULL, lon REAL NOT NULL, alt REAL NOT NULL, PRIMARY KEY (track, pos), FOREIGN KEY (track) REFERENCES tracks_track(id))'''])
