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

# testKalman.py

## Kalman Filter Prediction
    
x_hat_initial = np.random.rand(dim_state)
P_hat_initial = np.random.rand(dim_state,dim_state)
x_hat = np.zeros((num_samples,dim_state))
P_hat = np.zeros((num_samples,dim_state,dim_state))

for i in np.arange(num_samples):
    x_temp = np.dot(A,x_hat_initial)
    P_temp = np.dot(A,np.dot(P_hat_initial,A.transpose())) + W
    CP = np.dot(C,P_temp)
    PC = np.dot(P_temp,C.transpose())
    temp = np.dot(C,PC) + V
    temp = np.linalg.inv(temp)
    K = np.dot(PC,temp)
    x_hat[i] = x_temp + np.dot(K,(y[i] - np.dot(C,x_temp)))
    P_hat[i] = P_temp - np.dot(PC,np.dot(temp,CP))
    x_hat_initial = x_hat[i]
    P_hat_initial = P_hat[i]

## Kalman Filter Smoothing

t = 10
T = 10

As = np.zeros((T,dim_state,dim_state))
Ps = np.zeros((T,dim_state,dim_state))
Ss = np.zeros((T,dim_state,dim_state))
xs = np.zeros((T,dim_state))
base_index = t-T
xs_initial = x_hat[t]
Ps_initial = P_hat[t]

for i in np.arange(T-1,-1,-1):
    AP = np.dot(A,P_hat[i+base_index])
    temp = np.dot(AP,A.transpose()) + W
    temp = np.linalg.inv(temp)
    As[i] = np.dot(AP.transpose(),temp)
    Ss[i] = P_hat[i+base_index] - np.dot(As[i],AP)
    xs[i] = np.dot(As[i],xs_initial) + x_hat[i+base_index] - np.dot(As[i],np.dot(A,x_hat[i+base_index]))
    temp = np.dot(As[i],np.dot(Ps_initial,A.transpose()))+Ss[i]
    Ps[i] = 0.5*(temp+temp.transpose())
    Ps_initial = Ps[i]
    xs_initial = xs[i]

## Kalman Filter Parameter Learning

stop_flag = 'iter'
iter_max = 100
iter = -1
val = True
base_index = t-T

while (val):

    temp21 = np.zeros((T,dim_state,dim_state))
    temp12 = np.zeros((T,dim_state,dim_state))
    temp11 = np.zeros((T,dim_state,dim_state))
    yx = np.zeros((T,dim_obsrv,dim_state))
    xy = np.zeros((T,dim_state,dim_obsrv))
    yy = np.zeros((T,dim_obsrv,dim_obsrv))

    iter = iter + 1
    if stop_flag == 'iter':
        val = iter < iter_max

    temp11[0] = Ps[0] + np.dot(xs[0],xs[0].transpose())
    yx[0] = np.dot(np.reshape(y[0],(y[0].size,1)),np.reshape(xs[0].transpose(),(1,xs[0].size)))
    xy[0] = np.dot(np.reshape(xs[0],(xs[0].size,1)),np.reshape(y[0].transpose(),(1,y[0].size)))
    yy[0] = np.dot(np.reshape(y[0],(y[0].size,1)),np.reshape(y[0].transpose(),(1,y[0].size)))
    
    for i in np.arange(1,T):
        temp11[i] = Ps[i] + np.dot(xs[i],xs[i].transpose())
        temp21[i] = np.dot(As[i-1],Ps[i]) + np.dot(xs[i],xs[i-1].transpose())
        temp12[i] = np.dot(As[i],Ps[i-1]) + np.dot(xs[i-1],xs[i].transpose())
        yx[i] = np.dot(np.reshape(y[i],(y[i].size,1)),np.reshape(xs[i].transpose(),(1,xs[i].size)))
        xy[i] = np.dot(np.reshape(xs[i],(xs[i].size,1)),np.reshape(y[i].transpose(),(1,y[i].size)))
        yy[i] = np.dot(np.reshape(y[i],(y[i].size,1)),np.reshape(y[i].transpose(),(1,y[i].size)))

    temp12 = np.sum(temp12[1:],0)
    temp21 = np.sum(temp21[1:],0)
    yx_sum = np.sum(yx,0)
    xy_sum = np.sum(xy,0)
    yy_sum = np.sum(yy,0)
    An = np.dot(temp21,np.linalg.inv(np.sum(temp11,0)))
    Wn = (np.sum(temp11[1:],0)-np.dot(An,temp12)-np.dot(temp21,An.transpose()+np.dot(An,np.dot(np.sum(temp11[0:-1],0),An.transpose()))))/(T-1)
    Cn = np.dot(yx_sum,np.linalg.inv(np.sum(temp11,0)))
    Vn = (yy_sum-np.dot(C,xy_sum)-np.dot(yx_sum,Cn.transpose())+np.dot(Cn,np.dot(np.sum(temp11,0),Cn.transpose())))/T
    mu_0 = xs[0]
    Sigma_0 = Ps[0]
