#!/usr/bin/python3
import argparse
import logging
import sys
import os
sys.path.insert(1, os.path.abspath('../../pydma'))
import trackdb
from dbmeta import Db
import tracklist

trackdir = "~/.tiles"
tracklist.maxfile = 2

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
                print(filename)

if __name__ == "__main__":
    logging.basicConfig(filename='trackload.log', filemode='w', level=logging.DEBUG)
    loadsection('walking')

