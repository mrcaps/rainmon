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

import statsmodels.tsa.vector_ar.var_model
from statsmodels.tools.tools import ECDF
import pipeline
import numpy as np
import scipy.io
import pylab
import os

import matplotlib
matplotlib.rcParams.update({
    "font.size": 20,
    "lines.linewidth": 1,
    "ps.useafm": True,
    "pdf.use14corefonts": True,
    "text.usetex": True})

outdir = '../etc/tmp'

class VARPredictor:
	'''
	Vector autoregression model
	@see statsmodels.tsa.vector_ar.var_model.VAR
	'''
	def __init__(self,fulldata):
		'''
		@param fulldata: (time ticks)x(streams)
		'''
		self.fulldata = fulldata

	def outpredict(self,start,horizon):
		'''
		@param start: tick index to start prediction
		@param horizon: how many ticks into future to predict
		@return predictions, mse of predicted range
		'''
		temp = self.fulldata
		siz = temp.shape
		if start >= siz[0]:
			start = siz[0]-1
		mdl = statsmodels.tsa.vector_ar.var_model.VAR(temp)
		resm = mdl.fit()
		predicted = mdl.predict(resm.params,start,start+horizon)
		return predicted[1:,:]

class ConstantPredictor:
	'''
	"Predict last value" model
	'''
	def __init__(self, fulldata):
		self.fulldata = fulldata

	def outpredict(self,start,horizon):
		predicted = np.tile(self.fulldata[start-1,:],(horizon,1))

		mse = float('nan')
		if start + horizon < self.fulldata.shape[0]:
			mse = np.mean((predicted-self.fulldata[start:start+horizon,:])**2,1)
		return predicted, mse

def get_abilene_pipeline(fixstep):
	cypress = pipeline.CypressStage()
	spirit = pipeline.SpiritStage(ispca=False,thresh=0.01,ebounds=(0,1.1),startm=6)
	kalman = pipeline.KalmanStage(step_size=fixstep,lookahead_flag=0)
	pipe = pipeline.Pipeline()
	pipe.append_stage(cypress)
	pipe.append_stage(spirit)
	pipe.append_stage(kalman)
	return pipe

def run_hadoop(horizon):
	pipe = pipeline.get_default_pipeline()
	pipe.get_stages('KalmanStage')[0].lookahead_flag = 0
	pipe.get_stages('KalmanStage')[0].step_size = horizon

	input = {} 
	input['hosts'] = []
	for i in range(1, 65):
	    input['hosts'].append('cloud%d'%(i))

	#compression cache
	#input['start'] = '2011/11/22-15:00:00'
	#input['end'] = '2011/11/24-23:45:00'
	#metrics = ['iostat.disk.read_requests',
	#           'iostat.disk.write_requests',
	#            ]
	#input['metrics'] = metrics

	#cache a6af2b8bca225f6d8f99d832beec6d16
	input['start'] = '2011/10/11-10:00:00'
	input['end'] = '2011/10/16-10:00:00'
	metrics = ['iostat.disk.read_requests',
			   'iostat.disk.write_requests',
			   'iostat.disk.write_sectors',
			   'proc.meminfo.buffers',
			   'proc.meminfo.cached',
			   'proc.stat.cpu,type.system',
			   'proc.stat.cpu,type.user',
			   'proc.stat.cpu,type.iowait',
			   'proc.stat.cpu,type.nice',
			   'proc.net.bytes,direction.in',
			   'proc.net.bytes,direction.out',
			   'proc.net.packets,direction.in',
			   'proc.net.packets,direction.out',
			   'proc.stat.intr'
			   ]
	metrics = ['iostat.disk.read_requests',
	           'iostat.disk.write_requests',
	           'proc.meminfo.buffers',
	           'proc.meminfo.cached']
	input['metrics'] = metrics

	return pipe.run(input)	

def run_abilene(horizon):
	pipe = get_abilene_pipeline(horizon)

	input = {}
	input['data'] = []

	name = '../data/abilene-distro/Abilene.mat'
	data = scipy.io.loadmat(name)
	odnames = data['odnames']
	X = data['X2']
	X = np.log10(X+1)
	num_points, num_nodes = X.shape
	for i in np.arange(num_nodes):
		X[:,i] = X[:,i] - np.mean(X[:,i])
		X[:,i] = X[:,i]/np.sqrt(np.sum(X[:,i]**2))
	
	timestamp = data['utc2']
	X = X.T
	X = X[:,:2014]
	print "datashape", X.shape

	input['step'] = timestamp[1] - timestamp[0]
	input['mint'] = min(timestamp)
	input['maxt'] = max(timestamp)
	input['tsample'] = timestamp
	tsnames = [".".join(str(n[0][0]).split("-")) for n in odnames]
	input['ts_names'] = tsnames
	input['hosts'] = []
	input['data'] = X
	return pipe.run(input)

dataset = "abilene"

datacache = os.path.join(outdir,"predictcompare1.npz")
if os.path.exists(datacache):
	save = np.load(datacache)
	hvs_predict = save["hvs_predict"]
	hvs = save["hvs"]
	max_ind = save["max_ind"]
	mse_kalman = save["mse_kalman"]
	dta = save["dta"]
	predicted_const = save["predicted_const"]
	predicted_VAR = save["predicted_VAR"]
	mse_VAR = save["mse_VAR"]
	mse_const = save["mse_const"]
else:
	if dataset == "hadoop":
		horizon = 12
		output = run_hadoop(horizon)
	elif dataset == "abilene":
		horizon = 24
		output = run_abilene(horizon)
	else:
		print "Unknown dataset: %s" % dataset

	hvs = output["hvlog"]
	max_ind = np.max(output["mlog"])
	dta = hvs[0:max_ind,:]
	dta = dta.transpose()

	siz = dta.shape
	T = 50
	i = T

	mse_const = np.zeros(siz[0])
	mse_VAR = np.zeros(siz[0])

	predicted_const = np.copy(dta)
	predicted_VAR = np.copy(dta)

	pred_const = ConstantPredictor(dta)

	while(i < siz[0]-1):
		if (i+horizon+1) > siz[0]:
			horizon = siz[0]-1-i
		predicted_const[i+1:i+horizon+1], mse_const[i+1:i+horizon+1] = pred_const.outpredict(i,horizon)
		i = i+horizon

	i = T
	while(i < siz[0]-1):
		temp = dta[i-T:i,:]
		pred_VAR = VARPredictor(temp)
		if (i+horizon+1) > siz[0]:
			horizon = siz[0]-1-i

		predicted_VAR[i+1:i+horizon+1] = pred_VAR.outpredict(T,horizon)
		mse_VAR[i+1:i+horizon+1] = np.mean((predicted_VAR[i+1:i+horizon+1]-dta[i+1:i+horizon+1])**2,1)
		i = i+horizon

	hvs_predict = output["predict"]
	hvs = output["hvlog"]
	max_ind = np.max(output["mlog"])
	mse_kalman = np.mean((hvs[0:max_ind,:]-hvs_predict)**2,0)

	dta = dta[T+1:,:]
	predicted_const = predicted_const[T+1:,:]
	predicted_VAR = predicted_VAR[T+1:,:]
	mse_VAR = mse_VAR[T+1:]
	mse_const = mse_const[T+1:]
	mse_kalman = mse_kalman[T+1:]

	np.savez(datacache, hvs_predict=hvs_predict, hvs=hvs, \
		max_ind=max_ind, mse_kalman=mse_kalman, dta=dta, \
		predicted_const=predicted_const, predicted_VAR=predicted_VAR, \
		mse_VAR=mse_VAR, mse_const=mse_const)

saveall = False

for column in xrange(len(hvs_predict)):

	hv = hvs[column]
	hv_predict = hvs_predict[column]
	fig = pylab.figure(figsize=(6,4.5))
	fig.subplots_adjust(left=0.15,bottom=0.14,top=0.92,right=0.95)
	pylab.clf()
	#pylab.title("Predicted hidden variable " + str(column))
	pylab.subplot(111)
	p1 = pylab.plot(hv,'r-',linewidth=2, color=(1.0, 0.5, 0.5))
	p2 = pylab.plot(hv_predict,'b--',linewidth=2)
	pylab.xlim(0,hv.size)
	pylab.ylabel('Value')
	pylab.xlabel('Time Tick')
	pylab.legend(('Hidden Variable 1','Kalman Prediction'),loc=(0.08,0.8))
	if saveall:
		pylab.savefig(os.path.join(outdir, "kalman_predict_hv_%d.png" % column))
	if column == 0:
		pylab.savefig(os.path.join(outdir, "kalman_predict_hv_%d.pdf" % column))
		pylab.savefig(os.path.join(outdir, "kalman_predict_hv_%d.eps" % column))

	pylab.clf()
	pylab.subplot(111)
	p1 = pylab.plot(dta[:,column],'r-',linewidth=2, color=(1.0, 0.5, 0.5))
	p2 = pylab.plot(predicted_const[:,column],'b--',linewidth=2)
	pylab.xlim(0,mse_VAR.size)
	if saveall:
		pylab.legend(('Spirit Coefficients','Constant Predicted Coefficients'))
		pylab.savefig(os.path.join(outdir, "const_predict_hv_%d.png" % column))

	pylab.clf()
	pylab.plot(dta[:,column],'r-',linewidth=2, color=(1.0, 0.5, 0.5))
	pylab.plot(predicted_VAR[:,column],'b--',linewidth=2)
	pylab.xlim(0,mse_VAR.size)
	if saveall:
		pylab.legend(('Spirit Coefficients','VAR Predicted Coefficients'))
		pylab.savefig(os.path.join(outdir, "VAR_predict_hv_%d.png" % column))

pylab.clf()
#pylab.title("Mean Squared Prediction Error ")
pylab.subplot(111)
pylab.plot(mse_const,'g--',linewidth=2)
pylab.plot(mse_VAR,'r',linewidth=2, color=(1.0, 0.5, 0.5))
pylab.plot(mse_kalman,'b',linewidth=2)
pylab.xlim(0,mse_VAR.size)
pylab.legend(('Const.','VAR','Kalman'))
pylab.xlabel('Time Tick')
pylab.ylabel('Mean Squared Error')
pylab.savefig(os.path.join(outdir, "kalman_comparison.eps"))
pylab.savefig(os.path.join(outdir, "kalman_comparison.pdf"))

pylab.clf()
ax = pylab.subplot(111)

dmin = min(min(mse_const),min(mse_VAR),min(mse_kalman))
dmax = max(max(mse_const),max(mse_VAR),max(mse_kalman))
x = np.linspace(dmin,dmax)
maxx = 0.025
if maxx != None:
	x = np.linspace(0,maxx)
	np.append(x,[dmax])
pylab.plot(x,ECDF(mse_const)(x),'g--',linewidth=2)
pylab.plot(x,ECDF(mse_VAR)(x),'r',linewidth=2, color=(1.0, 0.5, 0.5))
pylab.plot(x,ECDF(mse_kalman)(x),'b',linewidth=2)
pylab.xlim((0,maxx))
pylab.legend(('Constant','VAR','Kalman'),loc='lower right')
pylab.xlabel('Mean Squared Error')
pylab.ylabel('Cumulative Frequency')

pylab.savefig(os.path.join(outdir, "kalman_comparison_cdf.eps"))
pylab.savefig(os.path.join(outdir, "kalman_comparison_cdf.pdf"))