#!/usr/bin/python
#########################################################################
# Author: Kai Ren
# Created Time: 2011-10-30 14:49:21
# File Name: ./test2.py
# Description: 
#########################################################################

import os
import sys
sys.path.append(os.path.abspath("../../data"))
import numpy
import matplotlib as mpl
import matplotlib.pyplot as plt
import pylab
from read_data import *
from cypress import * 
sys.path.append(os.path.abspath("../"))
from preprocess import *
import random

def flattenmetrics_nodes(dct, tstep):
    ks = dct.keys()

    #first pass: find minimum/maximum time
    mint = float("inf")
    maxt = float("-inf")
    for metric in ks:
        mdct = dct[metric]
        for i in range(len(mdct)):
            (ts, vs) = mdct[i]
            mint = min(mint, ts[0])
            maxt = max(maxt, ts[len(ts)-1])
    tsample = numpy.arange(mint,maxt,tstep)
    #do interpolation
    mnames = []
    vals = [0] * (len(ks) + 1)
    rn = 0
    for metric in ks:
        mnames.append(metric)
        mdct = dct[metric]
        vals[rn] = []
        for i in range(len(mdct)):
            (ts, vs) = mdct[i]
            vals[rn].append(numpy.interp(tsample, ts, vs))
        rn += 1
    return (mnames, vals, tsample)

def run_example():
    metrics = read_all_metric("../../datanode-data/", "cloud1.")
    (mnames, data, tsample) = flattenmetrics(metrics, 20)
    tlen = 800
    tsample = range(tlen)
    mpl.rcParams['font.size'] = 12
    for i in range(0, 1):
        cyp = Cypress(60, 1.8, 0)
        if len(data[i]) < 800:
            continue
        tdata = data[i][400:400+tlen] * 10
        lof, spike, hof = cyp.transform_retlof(tdata, 40)
#        pylab.figure(figsize=(8,8))
        fig = pylab.figure()
        pylab.subplots_adjust(hspace=.8)

        ax = pylab.subplot(4,1,1)
        ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(2))
        pylab.title("(a) Original timeseries data")
        pylab.plot(tsample, tdata, 'r-')
        ymin, ymax = pylab.ylim()
        ax = pylab.subplot(4,1,2)
        ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(2))
        pylab.title("(b) Smoothed trends using low pass filter")
        pylab.plot(tsample, lof, 'b-')
        pylab.ylim((ymin, ymax))
        ax = pylab.subplot(4,1,3)
        ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(2))
        pylab.title("(c) Spiky bursts detected after low pass filter")
        pylab.plot(tsample, spike, 'r-')
        ymin, ymax = pylab.ylim()
        ax = pylab.subplot(4,1,4)
        ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(2))
        pylab.title("(d) Residual data by removing (b) and (c) from raw data")
        pylab.plot(tsample, hof, 'b-')
        pylab.ylim((ymin, ymax))
        fig.text(0.07, 0.52, "CPU Utilization (%)", ha="right", va="center", size=16, rotation="vertical")
        fig.text(0.5, 0.02, "Time(Seconds)", ha="center", va="bottom", size=16)
        pylab.savefig("dec.%s.pdf"%(mnames[i]))
        pylab.show()

def run_correlation():
    step = 20
    metrics = read_all_metric("../../datanode-data/", "cloud")
    (mnames, data, tsample) = flattenmetrics_nodes(metrics, step)
    nnode = len(data[0])
    cyp = Cypress(60, 3, 0)

    for mi in range(0, 12):
        minv = float("inf") 
        maxv = float("-inf")
        cor = numpy.zeros((nnode, nnode))
#        for i in range(nnode):
#            for j in range(nnode):
#                cor[i][j] = cyp.correlation(data[mi][i], data[mi][j])
#                minv = min(minv, cor[i][j])
#                maxv = max(maxv, cor[i][j])

#        f = open("cor-%s.out"%(mnames[mi]), "w")
#        for i in range(nnode):
#            for j in range(nnode):
#                f.write("%.2f "%(cor[i][j]))
#            f.write('\n')
#        f.close()


        f = open("cor-%s.out"%(mnames[mi]), "r")
        for i in range(nnode):
            l = f.readline().rstrip().split()
            for j in range(nnode):
                cor[i][j] = float(l[j])
                minv = min(minv, cor[i][j])
                maxv = max(maxv, cor[i][j])
        f.close()

        print mnames[mi], minv, maxv
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        cax = ax1.imshow(cor, vmin=0, vmax=1)
        cbar = fig.colorbar(cax, ticks=[0, 0.5, 1])
        cbar.ax.set_yticklabels(["low", "medium", "high"])
        fontsize = 22
        ax = pylab.gca()
        for tick in cbar.ax.get_yticklabels():
           tick.set_fontsize(fontsize)
        xticks(fontsize=22)
        yticks(fontsize=22)
        plt.savefig("%s.png"%(mnames[mi]))

def findout_anomaly():
    files = os.listdir('./')
    for fn in files:
        if fn.endswith('.out'):
            f = open(fn, 'r')
            mat = []
            avgv = []
            ii = 0
            for line in f:
                items = line.split()
                nrow = []
                avgr = 0
                jj = 0
                for it in items:
                    if ii != jj:
                        nrow.append(float(it))
                        avgr += nrow[-1]
                    jj += 1
                avgv.append(avgr)
                mat.append(nrow)
                ii += 1
            avgstd = numpy.std(avgv)
            avgavg = numpy.average(avgv)
            index = 0
            print fn
            for avgr in avgv:
                if abs(avgr - avgavg) > avgstd:
                    print index, 
                index += 1
            print

def run_time_cor():
    step = 20
    metrics = read_all_metric("../../datanode-data/", "cloud")
    (mnames, data, tsample) = flattenmetrics_nodes(metrics, step)
    nnode = len(data[0])
    for mi in range(0, 12):
        plt.clf()
        for i in range(nnode):
            pylab.plot(tsample, data[mi][i], label='node%d'%(i))
        plt.legend(loc=2)
        plt.savefig("ts.%s.3.png"%(mnames[mi]))


def run_example_1():
    tdata = []
    f = open('data.txt', 'r')
    for l in f:
        ll = l.split()
        tdata.append(float(ll[2]))
    tlen = len(tdata)
    tsample = range(tlen)
    tdata = np.array(tdata)
    f.close()
    cyp = Cypress(60, 3, 0)
    lof, spike, hof = cyp.transform_retlof(tdata, 10)
    pylab.clf()
    pylab.subplots_adjust(hspace=.7)
    ax = pylab.subplot(4,1,1)
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(2))
    pylab.title("original")
    pylab.plot(tsample, tdata, 'r-')
    ymin, ymax = pylab.ylim()
    ax = pylab.subplot(4,1,2)
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(2))
    pylab.title("low pass")
    pylab.plot(tsample, lof, 'b-')
    pylab.ylim((ymin, ymax))
    ax = pylab.subplot(4,1,3)
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(2))
    pylab.title("spiky")
    pylab.plot(tsample, spike, 'g-')
    ymin, ymax = pylab.ylim()
    ax = pylab.subplot(4,1,4)
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(2))
    pylab.title("residual")
    pylab.plot(tsample, hof, 'g-')
    pylab.ylim((ymin, ymax))

#    pylab.savefig("dec.%s.png"%(mnames[i]))
    pylab.show()
    pylab.savefig("example.pdf")

if __name__ == '__main__':
   run_example()
#    run_correlation()
#    run_time_cor() 
#    findout_anomaly()
