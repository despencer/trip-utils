#!/usr/bin/python3

import sys
import os
import logging
from datetime import datetime, timedelta
from schemareader import Schema, SchemaReader
from pbreader import ProtobufReader
sys.path.insert(1, os.path.abspath('../geo'))
import obfdata
import geo

def unixtime(x):
    return datetime(1970,1,1)+timedelta(milliseconds=x)

obschema = { 'start':'header', 'structures':[
        { 'name':'header', 'factory': obfdata.Map, 'fields':
    { 1 : { 'name':'version' }, 18:{'name':'creation', 'factory':unixtime},
    6:{ 'name':'sections', 'factory':obfdata.Section, 'children':{     # map_section
        2:{'name':'name', 'factory':ProtobufReader.readutf8},
        5:{'name':'maplevels', 'structure':'maplevel' } } } } },
    { 'name':'maplevel', 'factory':obfdata.MapLevel, 'fields':{
            1:{'name':'maxzoom'}, 2:{'name':'minzoom'}, 3:{'name':'ibounds.left.value'}, 4:{'name':'ibounds.right.value'}, 5:{'name':'ibounds.top.value'}, 6:{'name':'ibounds.bottom.value'},
            7:{'name':'_node', 'lazy':'_nodereader', 'structure':'treenode' } } },
    { 'name':'treenode', 'factory':obfdata.MapNode, 'fields': {
        1:{'name':'ibounds.left.value', 'factory':ProtobufReader.readzigzag}, 2:{'name':'ibounds.right.value', 'factory':ProtobufReader.readzigzag},
        3:{'name':'ibounds.top.value', 'factory':ProtobufReader.readzigzag}, 4:{'name':'ibounds.bottom.value', 'factory':ProtobufReader.readzigzag},
        5:{'name':'data'}, 7:{'name':'_children', 'lazy':'_childrenreader','structure':'treenode'} }} ] }

def printnodes(indent, node):
    if len(node.children) == 0:
        return
    print('{0}Node at {1}, {2} children'.format(indent, node.bounds, len(node.children)))
    for c in node.children:
        printnodes(indent+'    ', c)

def main2(fname):
    schema = Schema(obschema)
#    schema.addformat({ 'structures':[ { 'name':'header', 'fields': { 6:{'print':4, 'children': { 5: { 'print':0 } } } } } ] } )
    with open(fname, 'rb') as obfile:
        reader = SchemaReader(obfile, schema)
        obfmap = reader.read()
        print('Map version {0}'.format(obfmap.version))
        for s in obfmap.sections:
            print('Section {0}'.format(s.name))
            for l in s.maplevels:
                print('Map level {0}-{1} at {2}'.format(l.minzoom, l.maxzoom, l.bounds))
                printnodes('    ', l.node)

if __name__ == '__main__':
    logging.basicConfig(filename='obinfo.log', filemode='w', level=logging.INFO)
    main2('/mnt/mobihome/maps/Russia_central-federal-district_asia_2.obf')

