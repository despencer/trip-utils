#!/usr/bin/python3

from datetime import datetime, timedelta, timezone
import argparse
from os import listdir
from os.path import isfile, join, splitext
import pandas as pd
from geopy import distance

class OziTrack:
    def __init__(self):
        pass

    @classmethod
    def loadfile(cls,filename):
        track = cls()
        points = pd.read_csv(filename, skiprows=5, header=0, names=['Latitude','Longitude','Start','Altitude','Timestamp','t1','t2'])
        points.drop(columns = ['t1','t2'], inplace=True)
        points['TS'] = points.apply(lambda x: OziTrack.convertdate(x.Timestamp, x.Altitude), axis=1)
        points['Altitude'] = points['Altitude'].apply(lambda x: OziTrack.convertaltitude(x))
        points['PLatitude'] = points['Latitude'].shift(1)
        points['PLongitude'] = points['Longitude'].shift(1)
        points['Dist'] = points.apply(lambda x: OziTrack.calcdist(x.Latitude, x.Longitude, x.PLatitude, x.PLongitude), axis=1)
        track.points = points
#        print(track.points)
        track.distance = points['Dist'].sum()
        if not pd.isnull(points['Altitude'].min()):
            track.date = points['TS'].min().date()
            track.duration = points['TS'].max() - points['TS'].min()
            track.velocity = track.distance / ( (track.duration.days * 24) + (track.duration.seconds/3600.0) )
        else:
            track.date = None
            track.duration = None
            track.velocity = None
        return track

    @classmethod
    def convertdate(cls, ozidate, alt):
        if alt == -777.0:
            return None
        return (datetime(1899, 12, 30, tzinfo=timezone.utc) + timedelta(days=ozidate)).astimezone()

    @classmethod
    def convertaltitude(cls, x):
        if x == -777.0 or x == 0:
            return None
        return x * 0.3048

    @classmethod
    def calcdist(cls, lat1, long1, lat2, long2):
        if pd.isnull(lat1) or pd.isnull(long1) or pd.isnull(lat2) or pd.isnull(long2):
            return None
        return distance.distance( (lat1, long1), (lat2, long2) ).km

parser = argparse.ArgumentParser(description='Show tracks info')
parser.add_argument('path', help='specifies path with tracks')
parser.add_argument('--sort', nargs='+')
args = parser.parse_args()

tracks = []
for f in listdir(args.path):
    file = join(args.path,f)
    if isfile(file):
        t = OziTrack.loadfile(file)
        tracks.append( (splitext(f)[0], t.distance, t.date, t.duration, t.velocity) )
tracks = pd.DataFrame(tracks, columns=['Name','Distance','Date','Duration','Velocity'])

if args.sort == None:
    tracks.sort_values(by='Distance', ascending=False, inplace=True)
else:
    tracks.sort_values(by=args.sort[0], inplace=True)
print(tracks.head(10).to_string(index=False))

# tracks = pd.DataFrame([f for f in listdir(args.path) if isfile(join(args.path,f))], columns=['Name'])
# t = OziTrack.loadfile(join(args.path,files[0]))
# print(t.points)
# print(t.distance)
# print(t.date)
#print(tracks)




