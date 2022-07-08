#!/usr/bin/python3

import sys
import os
import json
import matplotlib.pyplot as plt
sys.path.insert(1, os.path.abspath('../geo'))
import routing

def main(fways, fpic):
    print('loading')
    with open(fways) as jfile:
        mapdata = routing.MapJson.load(json.load(jfile))
    print('drawing')
    fig = plt.figure()
    ax = plt.subplot(1, 1, 1)
    for way in mapdata.ways:
        if way.tags['highway'] in ('trunk','trunk_link','primary', 'secondary', 'motorway'):
            lat = []
            lon = []
            for n in way.nodes:
                lat.append(n.point.lat.value)
                lon.append(n.point.lon.value)
            ax.plot(lon, lat, c='blue' if way.tags['highway'] in ('trunk','trunk_link','motorway') else 'black')
    fig.canvas.draw()
    fig.canvas.flush_events()
    fig.savefig(fpic)
    plt.close()

if __name__ == '__main__':
    main('mm.ways', '/mnt/mobihome/temp/mm.png')
