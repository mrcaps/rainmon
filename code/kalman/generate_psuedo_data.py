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

# generate_psuedo_data.py

import numpy as np

if __name__ == "__main__":

	num_samples = 2000
	dim_state = 4
	dim_obsrv = 2

	A = np.array([[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]])
	C = np.array([[1,0,0,0],[0,1,0,0]])

	Q = 0.1*np.eye(dim_state)
	R = 0.1*np.eye(dim_obsrv)

	initx = np.array([1,1,1,0])
	initV = 10*np.eye(dim_state)

	mu_Q = np.zeros(dim_state)
	mu_R = np.zeros(dim_obsrv)

	x = np.zeros((num_samples,dim_state))
	y = np.zeros((num_samples,dim_obsrv))

	x[0] = initx
	y[0] = np.dot(C,x[0]) + np.random.multivariate_normal(mu_R,R,1)

	for i in np.arange(1,num_samples):
	    x[i] = np.dot(A,x[i-1]) + np.random.multivariate_normal(mu_Q,Q,1)
	    y[i] = np.dot(C,x[i]) + np.random.multivariate_normal(mu_R,R,1)

	np.savez('xy_data.npz',x=x,y=y)
