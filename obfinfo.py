#!/usr/bin/python3

import logging
from datetime import datetime, timedelta
from schemareader import SchemaReader
from pbreader import ProtobufReader

def unixtime(x):
    return datetime(1970,1,1)+timedelta(milliseconds=x)

obschema = { 'start':'header', 'structures':[
        { 'name':'header', 'fields':
    { 1 : { 'format':'d' }, 18:{'format':'', 'factory':unixtime},
    6:{ 'print':4, 'children':{     # map_section
        2:{'format':'', 'factory':ProtobufReader.readutf8},
        5:{'format':'', 'default':'MapLevel', 'print':0, 'children':{
            1:{'format':'', 'name':'max'}, 2:{'format':'', 'name':'min'}, 3:{'format':'', 'name':'left'},
            4:{'format':'', 'name':'right'}, 5:{'format':'', 'name':'top'}, 6:{'format':'', 'name':'bottom'},
            7:{'format':'', 'name':'boxes', 'default':'TreeNode', 'structure':'treenode' } } } } } } },
    { 'name':'treenode', 'fields': {
        1:{'format':'', 'name':'left', 'factory':ProtobufReader.readzigzag}, 2:{'format':'', 'name':'right', 'factory':ProtobufReader.readzigzag},
        3:{'format':'', 'name':'top', 'factory':ProtobufReader.readzigzag}, 4:{'format':'', 'name':'bottom', 'factory':ProtobufReader.readzigzag},
        5:{'format':'', 'name':'shift'}, 7:{'format':'', 'name':'boxes'} }} ] }

def main2(fname):
    with open(fname, 'rb') as obfile:
        reader = SchemaReader(obfile, obschema)
        reader.read()

if __name__ == '__main__':
    logging.basicConfig(filename='obinfo.log', filemode='w', level=logging.INFO)
    main2('/mnt/mobihome/maps/Russia_central-federal-district_asia_2.obf')

