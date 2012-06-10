#!/usr/bin/python
#########################################################################
# Author: Kai Ren
# Created Time: 2011-10-30 14:28:13
# File Name: ./cypress.py
# Description: 
#########################################################################

import pylab
import numpy
import math

def fftshift(x):
    y = x.copy()
    y[:n/2], y[n/2:] = x[n/2:], x[:n/2]
    return y

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
