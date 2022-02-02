#!/usr/bin/python3
import argparse
import geomap

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show tracks info')
    parser.add_argument('map', help='specifies map definition')
    args = parser.parse_args()
    mapdesc = geomap.Map.load(args.map)
    mapdraw = mapdesc.makedraw()
    print("Updating {0}".format(mapdesc.name))
    print("Map at {0}".format(mapdraw.bounds))