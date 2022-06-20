#!/usr/bin/python3

import sys
import os
import json
import argparse
from collections import Counter
sys.path.insert(1, os.path.abspath('../geo'))
import routing

def makestat(mapdata):
    quants = Counter()
    for way in mapdata.ways:
        quants[way.tags['highway']] += 1
    print('Highways')
    for q in quants.most_common():
        print('    ', q[0], q[1])

def main(fways):
    print('loading', fways)
    with open(fways) as jfile:
        mapdata = routing.MapJson.load(json.load(jfile))
    print('calculating')
    makestat(mapdata)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show ways statistics')
    parser.add_argument('ways', help='a ways file')
    args = parser.parse_args()
    main(args.ways)