#!/usr/bin/python3

import time
import os
import os.path
from ozi import OziTrack
import pandas as pd
import tracklist

rfn = '/mnt/mobihome/gps-tracks/trackstat.txt'
# tracklist.maxfile = 2

def defaultperiod(tdate):
    return str(tdate.year)

def winterperiod(tdate):
    if tdate.month >= 6:
        return str(tdate.year+1)
    return str(tdate.year)

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
            { 'Name':lambda x: x[0:30].ljust(30,' '),
               'Distance': lambda x: "{:6.2f}".format(x),
               'Duration': lambda x: guard(x, lambda y: printduration(int(y.total_seconds()))),
               'Velocity': lambda x: "{:4.1f}".format(x)})

def printsection(tracks, rfile):
    rfile.write(printdf(tracks, 'Distance')+"\n")
    rfile.write(printdf(tracks, 'Duration')+"\n")
    rfile.write(printdf(tracks, 'Velocity')+"\n\n")

def dosection(path, rfile, showannual=True, period=None):
    print(f'Doing {path}')
    rfile.write('{0}\n{1}\n\n'.format(path, '='*len(path)))
    total = []
    section = {}
    if period == None:
        period = defaultperiod
    for filename in tracklist.trackiterator(path):
        t = OziTrack.loadfile(filename)
        row = (os.path.splitext(os.path.basename(filename))[0], t.distance, t.date, t.duration, t.velocity)
        p = period(t.date)
        if p not in section:
            section[p] = []
        section[p].append(row)
        total.append(row)
    if showannual:
        for t in section.values():
            printsection(t, rfile)
    printsection(total, rfile)

if __name__ == "__main__":
    with open(rfn, 'w') as rfile:
        dosection('walking', rfile)
        dosection('velo', rfile)
        dosection('car', rfile, showannual = False)
        dosection('travels', rfile, showannual = False)
        dosection('ski', rfile, showannual = True, period=winterperiod)
    print(f'see {rfn} for results')
