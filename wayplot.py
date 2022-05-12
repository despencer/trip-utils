#!/usr/bin/python3

import matplotlib.pyplot as plt

def main(ways, fpic):
    fig = plt.figure()
    ax = plt.subplot(1, 1, 1)
    ax.plot([54, 54, 55], [37, 38, 38], c='black')
    ax.plot([52, 52, 53], [38, 39, 39], c='black')
    fig.canvas.draw()
    fig.canvas.flush_events()
    fig.savefig(fpic)
    plt.close()

if __name__ == '__main__':
    main('mm.ways', '/mnt/mobihome/temp/mmways.png')
