from datetime import datetime, timedelta, timezone
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
        points['Dist'] = points.apply(lambda x: OziTrack.calcdist(x.Start, x.Latitude, x.Longitude, x.PLatitude, x.PLongitude), axis=1)
#        track.points = points
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
    def calcdist(cls, start, lat1, long1, lat2, long2):
        if start==1 or pd.isnull(lat1) or pd.isnull(long1) or pd.isnull(lat2) or pd.isnull(long2):
            return 0.0
        return distance.distance( (lat1, long1), (lat2, long2) ).km
