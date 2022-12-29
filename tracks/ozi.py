from datetime import date, datetime, timedelta, timezone
import pandas as pd
from geopy import distance
import os.path

class OziTrack:
    def __init__(self):
        pass

    @classmethod
    def loadfile(cls, filename, withpoints=False):
        track = cls()
        points = pd.read_csv(filename, encoding='cp1251', skiprows=5, header=0, names=['Latitude','Longitude','Start','Altitude','Timestamp','t1','t2'])
        points.drop(columns = ['t1','t2'], inplace=True)

        points['TS'] = points.apply(lambda x: OziTrack.convertdate(x.Timestamp, x.Altitude), axis=1)
        if pd.isna(points['TS'].min()):
#    for tracks from navigator without elevation recording
            trackdate = datetime.strptime(os.path.basename(filename)[0:8],'%Y%m%d')
            trackdate = datetime(trackdate.year, trackdate.month, trackdate.day, tzinfo=timezone.utc)
            points['TS'] = points.apply(lambda x: OziTrack.convertdate2(x.Timestamp, trackdate), axis=1)

        points['Altitude'] = points['Altitude'].apply(lambda x: OziTrack.convertaltitude(x))
        points['PLatitude'] = points['Latitude'].shift(1)
        points['PLongitude'] = points['Longitude'].shift(1)
        points['Dist'] = points.apply(lambda x: OziTrack.calcdist(x.Start, x.Latitude, x.Longitude, x.PLatitude, x.PLongitude), axis=1)
        track.distance = points['Dist'].sum()
        if not pd.isna(points['TS'].min()):
            track.date = points['TS'].min().date()
            if track.date != cls.convertdatefromfile(filename):
                  raise Exception(print(f'File {filename} has date {track.date}'))
            track.duration = points['TS'].max() - points['TS'].min()
            duration = ( (track.duration.days * 24) + (track.duration.seconds/3600.0) )
            if track.duration == None or duration == 0:
                track.velocity = None
            else:
                track.velocity = track.distance / duration
        else:
            track.date = cls.convertdatefromfile(filename)
            track.duration = None
            track.velocity = None
        if withpoints:
            track.points = points
        return track

    @classmethod
    def convertdate(cls, ozidate, alt):
        if alt == -777.0:
            return None
        return (datetime(1899, 12, 30, tzinfo=timezone.utc) + timedelta(days=ozidate)).astimezone()

    @classmethod
    def convertdate2(cls, ozidate, trackdate):
        candidate = (datetime(1899, 12, 30, tzinfo=timezone.utc) + timedelta(days=ozidate)).astimezone()
        totsec = (candidate - trackdate).total_seconds()
        if 0 <= totsec and totsec < 28*3600:
            return candidate
        return None

    @classmethod
    def convertdatefromfile(cls, filename):
      fdate = os.path.splitext(os.path.basename(filename))[0]
      return date(int(fdate[0:4]), int(fdate[4:6]), int(fdate[6:8]))

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
