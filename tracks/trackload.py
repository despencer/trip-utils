#!/usr/bin/python3
import argparse
import logging
import sys
import os
import hashlib
from datetime import date, datetime, timedelta, timezone, time
import pandas as pd
sys.path.insert(1, os.path.abspath('../../pydma'))
import trackdb
from dbmeta import Db
import tracklist
import ozi

# tracklist.maxfile = 2

def filehash(trackfile):
    md5 = hashlib.md5()
    with open(trackfile, 'rb') as file:
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        md5.update(file.read(size))
    return md5.digest()

def loadtrack(db, trackfile):
    name = os.path.splitext(os.path.basename(trackfile))[0]
    track = trackdb.DbTrack.getbyname(db, name)
    print('Loading ', name)
    trackdb.DbTrackPoint.cleartrack(db, track.id)
    ozitrack = ozi.OziTrack.loadfile(trackfile, withpoints=True)
    for p in ozitrack.points.itertuples(True, 'points'):
        otime = None if pd.isna(p.TS) else p.TS
        ctime = otime if otime != None else datetime.combine(ozitrack.date, datetime.min.time(), tzinfo=timezone.utc)
        altitude = None if pd.isna(p.Altitude) else p.Altitude
        trackdb.DbTrackPoint.create(db, track.id, p.Index+1, otime, ctime, p.Latitude, p.Longitude, altitude)
    db.finish()

def checktrack(db, trackfile):
    name = os.path.splitext(os.path.basename(trackfile))[0]
    track = trackdb.DbTrack.getbyname(db, name)
    hash = filehash(trackfile)
    if track == None:
        trackdb.DbTrack.create(db, name, hash, datetime.combine(ozi.OziTrack.convertdatefromfile(trackfile),time(0,0),tzinfo=timezone.utc) )
        return True
    else:
        if track.hash != hash:
            track.hash = hash
            track.update(db)
            return True
        else:
            return False

def loadsection(section):
    print(f'Doing {section}')
    with trackdb.open(section) as db:
        for filename in tracklist.trackiterator(section):
            if checktrack(db, filename):
                loadtrack(db, filename)

if __name__ == "__main__":
    logging.basicConfig(filename='trackload.log', filemode='w', level=logging.DEBUG)
    loadsection('walking')

