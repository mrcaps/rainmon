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

import matplotlib.patches as mpatches

import matplotlib
matplotlib.rcParams.update({
    "ps.useafm": True,
    "pdf.use14corefonts": True,
    "text.usetex": True})

import cypress
import spirit
import kalman

class Pipeline:
    def  __init__(self):
        self.stages = []

    def resize(self, num):
        self.stages = [None] * num

    def set_stage(self, stage_no, stage_func):
        if stage_no < len(self.stages):
            self.stages[stage_no] = stage_func

    def append_stage(self, stage_func):
        self.stages.append(stage_func)

    def run(self, input):
        output = None
        for stage in self.stages:
            print "Running stage: ", stage
            output = stage.run(input)
            input = output
        return output

class CypressStage:
	def __init__(self):
		self.cyp = cypress.Cypress()

	def run(self, input):
		step = input['step']
		output_ts = []
		for ts in input['data']:
			output_ts.append(self.cyp.transform(ts, step))
			output_ts[-1].append(ts)
		output = {}
		output['mint'] = input['mint']
		output['maxt'] = input['maxt']
		output['step'] = input['step']
		output['tsample'] = input['tsample']
		output['ts_names'] = input['ts_names']
		output['data'] = output_ts
		return output

class SpiritStage:
	def __init__(self, ispca=True,thresh=0.05,startm=3,ebounds=(0.9995, 1),vlambda=0.99,pcafixk=False):
		self.ispca = ispca
		self.thresh = thresh
		self.startm = startm
		self.ebounds = ebounds
		self.vlambda = vlambda
		self.pcafixk = pcafixk

	def run(self, input):
		dmat = input["data"]

		if self.ispca:
			#lower -> retain more energy
			alg = spirit.PCA(self.thresh)
			if self.pcafixk:
				alg.setfixk(self.pcafixk)
		else:
			alg = spirit.Spirit(dmat.shape[1], self.startm, self.ebounds, self.vlambda)
		alg.run(dmat, True)

		output = input
		#time history of hidden variables
		output["hvlog"] = alg.gethvlog().T
		#time history of SPIRIT reconstructions
		output["reconlog"] = alg.getreclog()
		#final SPIRIT projection matrix
		output["projection"] = alg.W
		#number of hidden variables at each time tick
		mlog = alg.getmlog()
		output["mlog"] = mlog
		#maximum number of hidden variables
		output["maxhvs"] = int(max(mlog))
		#minimum number of hidden variables
		output["minhvs"] = int(min(mlog))

		return input

class KalmanStage:
	def run(self,input):

		data = input["hvlog"]
		max_ind = numpy.max(input["mlog"])
		data = data[0:max_ind,:]
		data = data.transpose()
		N,M = data.shape
		H = numpy.max(numpy.array([2,numpy.ceil(M/3)]))

		T = 50
		maxIter = 20
		step_size = 10

		A = numpy.eye(H, H)
		C = numpy.eye(M, H)
		Q = numpy.eye(H, H)
		R = numpy.eye(M, M)
		mu0 = numpy.random.randn(1,H)
		Q0 = Q
		model = kalman.lds_model(A,C,Q,R,mu0,Q0)
		z_hat,y_hat = kalman.learn_lds(model,data,T,H,step_size,maxIter)

		output = input
		output["predict"] = y_hat.transpose()
		output["smooth"] = z_hat.transpose()

		return input

class DrawStage:
    def __init__(self, outdir, fixymax):
        self.outdir = outdir
        self.fixymax = fixymax

    def run(self, input):
        outdir = self.outdir

        pdb.set_trace()
        
        if "hvlog" in input:
            hvs = input["hvlog"]
            hvsplot = len(hvs)
            if "maxhvs" in input:
                hvsplot = input["maxhvs"]
            for i in xrange(hvsplot):
                hv = hvs[i]
                pylab.clf()
                pylab.title("Hidden variable " + str(i))
                pylab.plot(hv, "r-")
                pylab.savefig(os.path.join(outdir, "hv.%d.png" % i))

        if "mlog" in input:
            pylab.clf()
            pylab.title("Number of hidden variables vs time")
            pylab.plot(input["mlog"], "r-")
            pylab.savefig(os.path.join(outdir, "hv.count.png"))            

        if "predict" in input:
            hvs_predict = input["predict"]
            hvs = input["hvlog"]
            max_ind = numpy.max(input["mlog"])
            mse = numpy.mean((hvs[0:max_ind,:]-hvs_predict)**2,0)
            pylab.clf()
            pylab.title("Kalman Filter Mean Squared Prediction Error ")
            pylab.subplot(111)
            pylab.plot(mse,'r')
            pylab.savefig(os.path.join(outdir, "kalman_mse.png"))
            for i in xrange(len(hvs_predict)):
                hv = hvs[i]
                hv_predict = hvs_predict[i]
                pylab.clf()
                pylab.title("Predicted hidden variable " + str(i))
                pylab.subplot(111)
                p1 = pylab.plot(hv,'r-')
                p2 = pylab.plot(hv_predict,'b--')
                pylab.legend(('Spirit Coefficients','Predicted Coefficients'))
                pylab.savefig(os.path.join(outdir, "predict_hv_%d.png" % i))
                
        return input

def get_default_pipeline():
	cypress = CypressStage()
	spirit = SpiritStage(ispca=False,thresh=0.01,ebounds=(0.96,1.1),startm=3)
	kalman = KalmanStage()
	pipeline = Pipeline()
	draw = DrawStage('../etc/tmp/abilene', False)
	#pipeline.append_stage(cypress)
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
	
	timestamp = data['utc2']
	input['data'] = X
	pipeline.run(input)
	W = input['projection']
	num_hvs = input['maxhvs']
	index = 0

	#plot all timeseries
	#for i in numpy.arange(num_nodes):
	#	pylab.clf()
	#	pylab.plot(numpy.arange(X[:,i].size)+1,X[:,i])
	# 	pylab.title("Plot of node flow " + str(i))
	# 	pylab.savefig(os.path.join('../etc/tmp/abilene_scatter',str(i)+".png"))

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
	# 	for j in numpy.arange(i+1,num_hvs):
	# 		pylab.clf()
	# 		pylab.scatter(W[:,i],W[:,j])
	# 		pylab.title("Scatter Plot of " + str(i)+" and "+str(j))
	# 		pylab.savefig(os.path.join('../etc/tmp/abilene_scatter',str(index)+".png"))
	# 		index += 1