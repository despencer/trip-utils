#!/usr/bin/python3
import argparse
import logging
import sys
import os
import hashlib
sys.path.insert(1, os.path.abspath('../../pydma'))
import trackdb
from dbmeta import Db
import tracklist

trackdir = "~/.tiles"
tracklist.maxfile = 2

def filehash(trackfile):
    md5 = hashlib.md5()
    with open(trackfile, 'rb') as file:
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        md5.update(file.read(size))
    return md5.digest()

def loadtrack(run, trackfile):
    name = os.path.splitext(os.path.basename(trackfile))[0]
    print('Loading ', name)

def checktrack(db, trackfile):
    name = os.path.splitext(os.path.basename(trackfile))[0]
    track = trackdb.DbTrack.getbyname(db, name)
    hash = filehash(trackfile)
    if track == None:
        trackdb.DbTrack.create(db, name, hash)
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
    dbpath = os.path.expanduser(trackdir)
    if not os.path.exists(dbpath):
        os.makedirs(dbpath)
    dbfile = os.path.join(dbpath, section + ".tracks")
    with Db(dbfile) as db:
        trackdb.init(db)
        with db.run() as run:
            for filename in tracklist.trackiterator(section):
                if checktrack(run, filename):
                    loadtrack(run, filename)

if __name__ == "__main__":
    logging.basicConfig(filename='trackload.log', filemode='w', level=logging.DEBUG)
    loadsection('walking')

