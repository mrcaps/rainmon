#!/usr/bin/python

#Copyright (c) 2012, Carnegie Mellon University.
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions
#are met:
#1. Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#3. Neither the name of the University nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.

#SPIRIT in python, based heavily on SPIRIT implementation from Papadimitriou2005
#@author ishafer

from numpy import *

class Spirit:
    #n: number of dimensions
    #m: number of starting dimensions
    def __init__(self, n, m=3, ebounds=(0.9995, 1), vlambda=0.99):
        self.n = n
        self.vlambda = vlambda
        #retain between these fractions of the energy
        #self.energy = (0, 1)
        self.energy = ebounds
        self.m = m
        self.holdOffTimeBegin = 2
        self.holdOffTimeNormal = 100
        self.holdOffTime = self.holdOffTimeBegin

        self.W = eye(n)
        self.Y = None
        #energy of eigenvalues
        self.d = 0.01*ones((n,1))
        self.sumYSq = 0
        self.sumXSq = 0
        self.lastChangeAt = 1
        self.tick = 0
        
        self.reclog = None

    #Get the QR decomposition of m
    # Spirit uses the Gram-Schmidt process
    def qr(self, m):
        return linalg.qr(m)
    
    def changem(self, delta):
        doit = True
        doit &= self.lastChangeAt < self.tick - self.holdOffTime 
        doit &= self.m < self.n
        if delta < 0:
            doit &= self.m > 1
        
        if doit:
            print "Changing m from %d to %d (ratio %g)" % \
                (self.m, self.m + delta, self.sumYSq/self.sumXSq)
            self.lastChangeAt = self.tick
            self.m = self.m + delta
    
    def step(self, row):
        self.tick += 1
        if self.tick == 100:
            self.holdOffTime = self.holdOffTimeNormal

        x = row
        for j in xrange(self.m):
            (self.W[:,j], self.d[j], x) = self.updateW(x, self.W[:,j], self.d[j])
        self.W[:,0:self.m] = self.qr(self.W[:,0:self.m])[0]
        
        #projection to m-dimensional space (hidden variables)
        self.Y = dot(self.W[:,0:self.m].T, row)
        
        #reconstruction
        xProj = dot(self.W[:,0:self.m], self.Y)
        
        #xOrth = row - xProj
        #error = sum(power(xOrth,2))/sum(power(row,2))
        self.sumYSq = self.vlambda * self.sumYSq + sum(power(self.Y,2))
        self.sumXSq = self.vlambda * self.sumXSq + sum(power(row,2))
        
        if self.sumYSq < self.energy[0]*self.sumXSq:
            self.changem(1)
        elif self.sumYSq > self.energy[1]*self.sumXSq:
            self.changem(-1)
            
        return (self.Y, xProj)
        
    def updateW(self, oldx, oldw, oldd):
        y = dot(oldw.T, oldx)
        d = (self.vlambda*oldd + y*y)[0]
        #multiply() isn't necessary, but useful for compat with matrix
        e = oldx - multiply(oldw, y)
        w = oldw + multiply(e, y / d)
        x = oldx - multiply(w, y)
        w = w / linalg.norm(w)
        return (w, d, x)
        
    def getreclog(self):
        if None == self.reclog:
            print "Reconstruction log not saved."
        return self.reclog

    def gethvlog(self):
        if None == self.ylog:
            print "Hidden variable log not saved."
        return self.ylog

    def getmlog(self):
        if None == self.mlog:
            print "Number of hidden variables log not saved"
        return self.mlog

    def getcenter(self):
        return None
        
    def run(self, data, save):
        nrows = 0
        nsteps = 1e6 #number of steps to stop at
        maxsteps = min(nsteps, data.shape[0])
        
        if save:
            #number of principal components might change...
            #keep track of reconstruction
            reclog = zeros((maxsteps, data.shape[1]))
            #keep track of number of principal components
            mlog = zeros((maxsteps))
            #keep track of values of hidden variables
            ylog = zeros((maxsteps, data.shape[1]))
        
        for row in data:
            (Y, recon) = self.step(row)
            reclog[nrows,:] = recon
            mlog[nrows] = self.m
            ylog[nrows,:Y.shape[0]] = Y
            
            nrows += 1
            if nrows == nsteps:
                break
                
        if save:
            self.reclog = reclog
            self.mlog = mlog
            self.ylog = ylog