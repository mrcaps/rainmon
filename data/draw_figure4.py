#!/usr/bin/python
import os
import sys
import numpy
import matplotlib as mpl
import matplotlib.pyplot as plt
import pylab
import math

import matplotlib
matplotlib.rcParams.update({
    "ps.useafm": True,
    "pdf.use14corefonts": True,
    "text.usetex": True})

class Cypress:
    #lof_m : cut-off frequency for LoF Trickles
    #spike_th : nosie threshold to get Spike Trickles
    #hif_k : the dimension of matrix to reduce for HiF trikles
    def __init__(self, lof_m=60, spike_th=3, hif_k=0):
        self.lof_m = lof_m
        self.spike_th = spike_th
        self.hif_k = hif_k

    def transform(self, vals, step):
        lof = self.low_pass_filter(vals, step)
        rem = vals - lof
        spike = self.spike_filter(rem)
        hof = rem - spike
        #edit 12/7: add residual to lowpass
        return [lof+hof, spike, hof]

    def transform_retlof(self, vals, step):
        lof = self.low_pass_filter(vals, step)
        rem = vals - lof
        spike = self.spike_filter(rem)
        hof = rem - spike
        return [lof, spike, hof]

    def low_pass_filter(self, x, dt):
        rc = dt * self.lof_m / math.pi
        alpha = dt / (rc + dt)
        y = [0] * len(x)
        y[0] = x[0]
        for i in range(1, len(x)):
            y[i] = alpha * x[i] + (1 - alpha) * y[i-1]
        return y

    def spike_filter(self, x):
        threshold = abs(numpy.std(x)) * self.spike_th
        y = [0] * len(x)
        for i in range(len(x)):
            if abs(x[i]) > threshold:
                y[i] = x[i]
        return y

    def dis(self, x):
      sum = 0.0
      for xx in x:
        sum += xx * xx
      return math.sqrt(sum)

    def dot(self, x, y):
      sum = 0.0
      for i in range(len(x)):
        sum += x[i] * y[i]
      return sum

    def correlation(self, x, y):
      return self.dot(x/self.dis(x), y/self.dis(y))

    def downsampling(self, x, step):
        return x[0:len(x):step]

def run_example():
    cyp = Cypress(60, 1.8, 0)
    tdata = []
    tsample = []
    f = open('figure4.dat', 'r')
    for l in f:
        its = l.split()
        tsample.append(int(its[0]))
        tdata.append(float(its[1]))
    f.close()
    tdata = numpy.array(tdata)
    tsample = numpy.array(tsample)
    lof, spike, hof = cyp.transform_retlof(tdata, 40)
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
    fig.text(0.07, 0.52, "CPU Utilization (percent)", ha="right", va="center", size=16, rotation="vertical")
    fig.text(0.5, 0.02, "Time (seconds)", ha="center", va="bottom", size=16)
    pylab.savefig("figure4.pdf")
    pylab.show()

if __name__ == '__main__':
   run_example()

