#!/usr/bin/python3

import sys
import os
import json
import math
import logging
import argparse
sys.path.insert(1, os.path.abspath('../../pydma'))
from dbmeta import DbPackaging

def main(params):
    

if __name__ == '__main__':
    logging.basicConfig(filename='loadtracks.log', filemode='w', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Loads tracks into db')
    parser.add_argument('params', help='parameter file (json)')
    args = parser.parse_args()
    
    main(args.params)