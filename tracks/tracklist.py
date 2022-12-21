import os
import os.path

basedirs = ['/mnt/mobihome/gps-tracks/archive/personal', '/mnt/mobihome/gps-tracks/exchange/personal']
maxfile = 0

def diriterator(dirname):
    print(f'\tDoing {dirname}')
    tracks = 0
    for f in os.listdir(dirname):
        filename = os.path.join(dirname, f)
        if os.path.isfile(filename):
            if len(os.path.splitext(f)[0]) >= 8:
                tracks += 1
                yield filename
        else:
            for subfilename in diriterator(filename):
                yield subfilename
        if maxfile > 0 and maxfile <= tracks:
            break

def trackiterator(section):
    for base in basedirs:
        dirname = os.path.join(base, section)
        if os.path.isdir(dirname):
            for filename in diriterator(dirname):
                yield filename
