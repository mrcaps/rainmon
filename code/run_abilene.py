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

# run_abilene.py

import numpy
import scipy
from scipy import io
import urllib
import pylab
import matplotlib.pyplot as plt
import json
import os
import pickle
import os.path
from rescache import Cache

import matplotlib.patches as mpatches

import matplotlib
matplotlib.rcParams.update({
    "ps.useafm": True,
    "pdf.use14corefonts": True,
    "text.usetex": True})

import cypress
import spirit
import kalman

from pipeline import Pipeline, CypressStage, SpiritStage, KalmanStage, DrawStage

def get_default_pipeline():
    cypress = CypressStage()
    spirit = SpiritStage(ispca=False,thresh=0.01,ebounds=(0.96,1.1),startm=3)
    kalman = KalmanStage()
    pipeline = Pipeline()
    draw = DrawStage('../etc/tmp/abilene', False)
    pipeline.append_stage(cypress)
    pipeline.append_stage(spirit)
    #pipeline.append_stage(kalman)
    #pipeline.append_stage(draw)
    return pipeline

if __name__ == '__main__':
    import matplotlib
    matplotlib.rcParams.update({"font.size": 18})

    pipeline = get_default_pipeline()
    input = {}
    input['data'] = []

    name = '../data/abilene-distro/Abilene.mat'
    data = scipy.io.loadmat(name)
    odnames = data['odnames']
    X = data['X2']
    X = numpy.log10(X+1)
    num_points, num_nodes = X.shape
    for i in numpy.arange(num_nodes):
        X[:,i] = X[:,i] - numpy.mean(X[:,i])
        X[:,i] = X[:,i]/numpy.sqrt(numpy.sum(X[:,i]**2))
    
    timestamp = [t[0] for t in data['utc2']]
    input['data'] = X.T
    input['tsample'] = timestamp
    input['mint'] = min(timestamp)
    input['maxt'] = max(timestamp)
    input['step'] = (max(timestamp) - min(timestamp)) / len(input['data'][0])

    tsnames = []
    for n in data['odnames']:
        narr = str(n[0][0]).split("-")
        tsnames.append(narr[1] + "." + narr[0])
    input['ts_names'] = tsnames

    output = pipeline.run(input)

    W = output['projection']
    num_hvs = output['maxhvs']
    index = 0

    #dumpoutput = [[[],[],[],darr] for darr in output['data'].T]
    dumpoutput = output['data']
    origoutput = output['data']
    output['data'] = dumpoutput
    outdir = "../etc/tmp/cache/abilene"
    cache = Cache(outdir)
    cache.write(output)

    output['data'] = origoutput

    #plot all timeseries
    #for i in numpy.arange(num_nodes):
    #    pylab.clf()
    #    pylab.plot(numpy.arange(X[:,i].size)+1,X[:,i])
    #     pylab.title("Plot of node flow " + str(i))
    #     pylab.savefig(os.path.join('../etc/tmp/abilene_scatter',str(i)+".png"))

    fig = pylab.figure()
    fig.subplots_adjust(left=0.15)
    ax = fig.add_subplot(111)
    MSIZE = 7
    ax.plot(W[:,0],W[:,1],"go",markersize=MSIZE)
    c = mpatches.Circle((-0.03, -0.03), 0.025, color="y", ec="r", lw=3)
    ax.add_patch(c)
    pylab.xlabel('$W_{:,1}$')
    pylab.ylabel('$W_{:,2}$')
    ax.annotate("Router IPLS",
            xy=(-0.04, -0.05), xycoords='data',
            xytext=(-0.05, -0.3), textcoords='data',
            arrowprops=dict(arrowstyle="->",
                            connectionstyle="arc3"),
            )
    pylab.savefig('abilene_scatter.pdf')
    pylab.savefig('abilene_scatter.eps')

    pylab.clf()
    fig.subplots_adjust(left=0.15)
    pylab.plot(numpy.arange(X[:,0].size)+1,X[:,44:55])
    pylab.xlim((0,num_points))
    pylab.xlabel("Time (tick)")
    pylab.ylabel("Normalized Packets (count)")
    pylab.savefig('abilene_anomaly.pdf')
    pylab.savefig('abilene_anomaly.eps')

    # for i in numpy.arange(num_hvs):
    #     for j in numpy.arange(i+1,num_hvs):
    #         pylab.clf()
    #         pylab.scatter(W[:,i],W[:,j])
    #         pylab.title("Scatter Plot of " + str(i)+" and "+str(j))
    #         pylab.savefig(os.path.join('../etc/tmp/abilene_scatter',str(index)+".png"))
    #         index += 1