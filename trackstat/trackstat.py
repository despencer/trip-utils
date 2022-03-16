#!/usr/bin/python3

import time
import os
import os.path
from ozi import OziTrack
import pandas as pd

base = '/mnt/mobihome/gps-tracks/archive/personal'
rfn = '/mnt/mobihome/gps-tracks/trackstat.txt'
maxfile = 0

def loadtracks(dirname):
    print(f'\tDoing {dirname}')
    tracks = []
    for f in os.listdir(dirname):
        file = os.path.join(dirname, f)
        if os.path.isfile(file):
            t = OziTrack.loadfile(file)
            tracks.append( (os.path.splitext(f)[0], t.distance, t.date, t.duration, t.velocity) )
        if maxfile > 0 and maxfile <= len(tracks):
            break
    return tracks

def printdf(tracks, sortby):
    df = pd.DataFrame(tracks, columns=['Name','Distance','Date','Duration','Velocity'])
    df.sort_values(by=sortby, ascending=False, inplace=True)
    return df.head(10).to_string(index=False, columns=['Name','Distance','Duration','Velocity'])

def dosection(path, rfile):
    print(f'Doing {path}')
    rfile.write('{0}\n{1}\n\n'.format(path, '='*len(path)))
    dirname = os.path.join(base, path)
    for d in os.listdir(dirname):
        sub = os.path.join(dirname, d)
        if os.path.isdir(sub):
            tracks = loadtracks(sub)
            rfile.write(printdf(tracks, 'Distance')+"\n\n")

if __name__ == "__main__":
    with open(rfn, 'w') as rfile:
        dosection('walking', rfile)
    print(f'see {rfn} for results')
