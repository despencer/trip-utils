#!/usr/bin/python3
import argparse
import logging
import sys
import os
sys.path.insert(1, os.path.abspath('../geo'))
sys.path.insert(1, os.path.abspath('../../pydma'))
import tiles

if __name__ == '__main__':
    logging.basicConfig(filename='update.log', filemode='w', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Tile database add version')
    parser.add_argument('storage', help='tile storage')
    parser.add_argument('provider', help='provider')
    parser.add_argument('parameter', help='version parameter')
    args = parser.parse_args()
    with tiles.TileCache(args.storage) as cache:
        cache.addversion(args.provider, args.parameter)


