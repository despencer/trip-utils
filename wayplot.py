#!/usr/bin/python3

import json
import matplotlib.pyplot as plt

def main(fways, fpic):
    with open(fways) as jfile:
        jways = json.load(jfile)['ways']
    fig = plt.figure()
    ax = plt.subplot(1, 1, 1)
    for way in jways:
        lat = []
        lon = []
        for p in way['points']:
            lat.append(p['lat'])
            lon.append(p['lon'])
        ax.plot(lon, lat, c='black')
    fig.canvas.draw()
    fig.canvas.flush_events()
    fig.savefig(fpic)
    plt.close()

if __name__ == '__main__':
    main('mm.ways', '/mnt/mobihome/temp/mmways.png')
