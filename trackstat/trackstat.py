#!/usr/bin/python3

import time
import os
import os.path
from ozi import OziTrack
import pandas as pd

basedirs = ['/mnt/mobihome/gps-tracks/archive/personal', '/mnt/mobihome/gps-tracks/exchange/personal']
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

def printduration(seconds):
    hours, rem = divmod(seconds, 3600)
    return "{:2}:{:02}".format(int(hours),int(rem/60))

def guard(x, formatter):
    if pd.isnull(x):
        return "-"
    return formatter(x)

def printdf(tracks, sortby):
    df = pd.DataFrame(tracks, columns=['Name','Distance','Date','Duration','Velocity'])
    df.sort_values(by=sortby, ascending=False, inplace=True)
    return df.head(10).to_string(index=False, columns=['Name','Distance','Duration','Velocity'], formatters = 
            { 'Name':lambda x: x[0:24].ljust(24,' '),
               'Distance': lambda x: "{:6.2f}".format(x),
               'Duration': lambda x: guard(x, lambda y: printduration(y.seconds)),
               'Velocity': lambda x: "{:4.1f}".format(x)})

def printsection(tracks, rfile):
    rfile.write(printdf(tracks, 'Distance')+"\n")
    rfile.write(printdf(tracks, 'Duration')+"\n")
    rfile.write(printdf(tracks, 'Velocity')+"\n\n")

def dosection(path, rfile):
    print(f'Doing {path}')
    rfile.write('{0}\n{1}\n\n'.format(path, '='*len(path)))
    total = []
    for base in basedirs:
        dirname = os.path.join(base, path)
        if os.path.isdir(dirname):
            for d in os.listdir(dirname):
                sub = os.path.join(dirname, d)
                if os.path.isdir(sub):
                    tracks = loadtracks(sub)
                    total.extend(tracks)
                    printsection(tracks, rfile)
    printsection(total, rfile)

if __name__ == "__main__":
    with open(rfn, 'w') as rfile:
        dosection('walking', rfile)
        dosection('velo', rfile)
    print(f'see {rfn} for results')
