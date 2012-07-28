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

# run _826_kalman.py

import os,sys
sys.path.append(os.path.abspath("../"))
import numpy as np
from preprocess import *
from analysis import *
from lds import *
import matplotlib.pyplot as plt

if __name__ == "__main__":
	dm = DataMatrix('../../../826-data/data/')
	dm.load()
	# chunk of data to get in secs
	dm.flatten(300)
	dm.transform_all()
	dm.print_stats()
	y_noise = dm.get_data()
	T = 50
	maxIter = 20
	step_size = 20

	#index = np.array([0,4,6,7,8])
	#index = np.array([0,1,3,6,7,8,10,11,12,13,16,19,21,24])
	index = np.array([0,3,6,7,8,11,12,16,19,24])
	dim_obsrv = index.size
	H = index.size
	y_noise = y_noise[:,index]

	N,M = y_noise.shape
	H = M

	# A = np.array([[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]])
	# C = np.array([[1,0,0,0],[0,1,0,0]])
	# Q = 0.1*np.eye(H)
	# R = 0.1*np.eye(M)
	# mu0 = np.array([10,10,1,0])

	A = np.eye(H, H) + 0*np.random.randn(H, H)
	C = np.eye(M, H) + 0*np.random.randn(M, H)
	Q = np.eye(H, H)
	R = np.eye(M, M)
	mu0 = np.random.randn(1,H)

	Q0 = Q
	model = lds_model(A,C,Q,R,mu0,Q0)

	z_hat,y_hat = learn_lds(model,y_noise,T,H,step_size,maxIter)

	for i in np.arange(index.size):
	    loc = 'figs/' + str(i) + '.png'
	    plot_recon(loc,y_noise[:,i],y_hat[:,i],thetitle="Actual vs Predicted", showlegend=True)
