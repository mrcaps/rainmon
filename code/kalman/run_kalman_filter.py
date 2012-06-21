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

# run_kalman_filter.py

import numpy as np
import matplotlib.pyplot as plt
import kalman
import pdb

name = 'xy_data.npz'
data = np.load(name)

x_noise = data['x']
y_noise = data['y']

T = 100
maxIter = 10
H = 4
step_size = 20

## Model Initialization
N,M = y_noise.shape

# A = np.array([[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]])
# C = np.array([[1,0,0,0],[0,1,0,0]])
# Q = 0.1*np.eye(H)
# R = 0.1*np.eye(M)
# mu0 = np.array([10,10,1,0])

A = 0.1*np.eye(H, H) + 0*np.random.randn(H, H)
C = 0.1*np.eye(M, H) + 0*np.random.randn(M, H)
Q = np.eye(H, H)
R = np.eye(M, M)
mu0 = np.random.randn(1,H)

Q0 = Q
model = kalman.lds_model(A,C,Q,R,mu0,Q0)

z_hat,y_hat = kalman.learn_lds(model,y_noise,T,H,step_size,maxIter)

plt.figure(1)
plt.scatter(y_noise[:,0],y_noise[:,1])
plt.scatter(y_hat[:,0],y_hat[:,1],c='r')
plt.title('Predicted vs Actual Location')

plt.figure(2)
plt.plot(np.sqrt(np.sum((y_hat-y_noise)**2,1)))
plt.title('Location Error')
plt.show()
