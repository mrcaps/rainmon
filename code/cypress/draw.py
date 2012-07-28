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

#########################################################################
# Author: Kai Ren
# Created Time: 2011-11-30 21:24:10
# File Name: ./draw.py
# Description: 
#########################################################################
import math
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    f = open('err_recon1', 'r')
    results = [[],]
    index = []
    i = 0
    for l in f:
        if l.startswith('-'):
            i += 1
            index.append(l[1:])
            results.append([])
        else:
            results[i].append(float(l))
    f.close()

    mean_arr = []
    std_arr = []
    for i in range(1, len(results)):
        mean = 0
        for v in results[i]:
            mean += v
        mean /= len(results[i])
        std = 0
        for v in results[i]:
            std += (v - mean) * (v - mean)
        std = math.sqrt(std)
        mean_arr.append(mean)
        std_arr.append(std)

    print mean_arr
    width = 0.35
    ind = np.arange(len(mean_arr))
    #plt.clf()
    fig = plt.figure()
    fig.subplots_adjust(bottom=0.18)
    #fig = plt.figure()
    #ax1 = fig.add_subplot(111)
    p1 = plt.bar(ind, mean_arr, width, color='r', yerr=std_arr)
    plt.ylabel('Reconstruction Accuracy', fontsize=22)
    plt.xlabel('Time Scale (Minutes)', fontsize=20)
    #plt.title('Scores by group and gender')
    plt.ylim((0.6, 1))
    plt.xticks(ind+width/2., index, fontsize=22)
    plt.yticks(np.arange(0.6,1.01,0.1), fontsize=22)
    #plt.legend( (p1[0]), ('Reconstruction Error') )
    #plt.show()
    plt.savefig("timescale.png")
