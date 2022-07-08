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
    dist = Counter()
    for way in mapdata.ways:
        quants[way.tags['highway']] += 1
        dist[way.tags['highway']] += way.length()
    print('Highway numbers')
    for q in quants.most_common():
        print('    ', q[0], q[1])
    print('Highway length')
    for d in dist.most_common():
        print('    {0} {1:.3f}'.format(d[0], d[1]/1000))

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