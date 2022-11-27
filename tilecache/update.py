#!/usr/bin/python3
import argparse
import sys
import os
sys.path.insert(1, os.path.abspath('../geo'))
import geo

def update(storage, bounds, level):
    print('Checking storage ', args.storage)
    print('Updating ', bounds, ' at ', level)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tile database updates')
    parser.add_argument('storage', help='tile storage')
    parser.add_argument('bounds', help='bounds to update')
    parser.add_argument('level', help='bounds to update')
    args = parser.parse_args()
    update(args.storage, geo.Rectangle.parse(args.bounds), int(args.level))
