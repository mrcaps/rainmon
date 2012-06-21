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

# lds.py
## Here we implement the complete Kalman Filter.

import numpy as np
import scipy as sp
from scipy import linalg
import pdb

## This is the main Kalman Filtering function.
## This calls everything and returns the final answer.

def kalman(y,dim_state,T,iter_max):

    num_samples,dim_obsrv = y.shape
    x_hat_initial = np.random.rand(dim_state)
    P_hat_initial = np.eye(dim_state)

    A = np.eye(dim_state)+0*np.random.rand(dim_state,dim_state)
    C = np.eye(dim_obsrv,dim_state)+0*np.random.rand(dim_obsrv,dim_state)
    W = np.eye(dim_state)
    V = np.eye(dim_obsrv)
    mu = np.random.rand(dim_state)*0
    Sigma = np.eye(dim_state)

    x_hat = np.zeros((num_samples,dim_state))
    P_hat = np.zeros((num_samples,dim_state,dim_state))
    y_hat = np.zeros((num_samples,dim_obsrv))
    An = np.zeros((num_samples,dim_state,dim_state))
    Wn = np.zeros((num_samples,dim_state,dim_state))
    Cn = np.zeros((num_samples,dim_obsrv,dim_state))
    Vn = np.zeros((num_samples,dim_obsrv,dim_obsrv))
    mu_0 = np.zeros((num_samples,dim_state))
    Sigma_0 = np.zeros((num_samples,dim_state,dim_state))

    for i in np.arange(T-1,num_samples):
        An[i],Wn[i],Cn[i],Vn[i],mu_0[i],Sigma_0[i] = kalman_learning(y[(i-T+1):(i+1)],A,W,C,V,mu,Sigma,T,iter_max)
        A = An[i]
        W = Wn[i]
        C = Cn[i]
        V = Vn[i]
        mu = mu_0[i]
        Sigma = Sigma_0[i]
        x_hat[i],P_hat[i],temp = kalman_predict(y[i],A,C,W,V,x_hat_initial,P_hat_initial)
        y_hat[i] = np.dot(C,x_hat[i])
        x_hat_initial = x_hat[i]
        P_hat_initial = P_hat[i]
        
    return x_hat,y_hat,P_hat

## Kalman Filter Parameter Learning
## This functions implements the EM algorithm for parameter learning
def kalman_learning(y,A,W,C,V,mu_0,Sigma_0,T,iter_max):

    dim_state,dim_state = A.shape
    dim_obsrv,dim_state = C.shape

    An = A
    Cn = C
    Wn = W
    Vn = V
    oldlogli = -np.inf
    ratio = 1
    diff = 1
    CONV_BOUND = 1e-5

    iter = -1

    print isTiny(Sigma_0),isTiny(W),isTiny(V)

    while ((ratio > CONV_BOUND or diff > CONV_BOUND) and (iter < iter_max) and ((isTiny(Sigma_0) or isTiny(W) or isTiny(V))) != True):
        A_old = An
        C_old = Cn
        W_old = Wn
        V_old = Vn

        x_hat,P_hat,logli = kalman_predict(y,An,Cn,Wn,Vn,mu_0,Sigma_0)
        xs,Ez1z,Ezz = kalman_smoothing(x_hat,P_hat,An,Wn)
        
        xy = np.zeros((T,dim_state,dim_obsrv))
        yy = np.zeros((T,dim_obsrv,dim_obsrv))

        iter = iter + 1
        
        xy[0] = np.dot(np.reshape(xs[0],(xs[0].size,1)),np.reshape(y[0].transpose(),(1,y[0].size)))
        yy[0] = np.dot(np.reshape(y[0],(y[0].size,1)),np.reshape(y[0].transpose(),(1,y[0].size)))
    
        for i in np.arange(1,T):
            xy[i] = np.dot(np.reshape(xs[i],(xs[i].size,1)),np.reshape(y[i].transpose(),(1,y[i].size)))
            yy[i] = np.dot(np.reshape(y[i],(y[i].size,1)),np.reshape(y[i].transpose(),(1,y[i].size)))

        Ez1z = np.sum(Ez1z[0:-1],0)
        xy_sum = np.sum(xy,0)
        yy_sum = np.sum(yy,0)
        An = np.dot(Ez1z,np.linalg.inv(np.sum(Ezz,0)))
        tempW = np.dot(An,Ez1z.transpose())
        Wn = (np.sum(Ezz[1:],0)-tempW-tempW.transpose()+np.dot(An,np.dot(np.sum(Ezz[0:-1],0),An.transpose())))/(T-1)
        Cn = np.dot(xy_sum.transpose(),np.linalg.inv(np.sum(Ezz,0)))
        tempV = np.dot(Cn,xy_sum)
        Vn = (yy_sum-tempV-tempV.transpose()+np.dot(Cn,np.dot(np.sum(Ezz,0),Cn.transpose())))/T
        mu_0 = xs[0]
        Sigma_0 = Ezz[0]-np.dot(np.reshape(xs[0],(xs[0].size,1)),np.reshape(xs[0].transpose(),(1,xs[0].size)))

        logli = np.real(logli)
        diff = (logli - oldlogli)
        if (logli < oldlogli):
            print('Loglikelihood decreases!')

        ratio = (diff/logli)
        print diff, ratio, logli
        oldlogli = logli

    return An,Wn,Cn,Vn,mu_0,Sigma_0

## Kalman Filter Prediction

def kalman_predict(y,A,C,W,V,x_hat_initial,P_hat_initial):
    logli = 0
    dim_state,dim_state = A.shape
    if y.ndim == 1:
        dim_obsrv = y.size
        num_samples = 1
    else:
        num_samples,dim_obsrv = y.shape
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
        y_hat = np.dot(C,x_hat[i])
        err = (y[i]-y_hat)
        posdef = np.dot(err.transpose(),np.dot(temp,err))/2
        if posdef < 0:
            print("Not Positive Def")
        x_hat_initial = x_hat[i]
        P_hat_initial = P_hat[i]
        logli = logli - dim_state/2*np.log(2*np.pi) + logdet(temp)/2 - posdef;

    return x_hat,P_hat,logli

## Kalman Filter Smoothing

def kalman_smoothing(x_hat,P_hat,A,W):

    T,dim_state = x_hat.shape
    T,dim_state,dim_state = P_hat.shape

    xs = np.zeros((T,dim_state))
    Ez1z = np.zeros((T,dim_state,dim_state))
    Ezz = np.zeros((T,dim_state,dim_state))

    xs[-1] = x_hat[-1]
    Ps = P_hat[-1]
    PA = np.dot(P_hat[-1],A.transpose())
    temp = np.dot(A,PA) + W
    temp = np.linalg.inv(temp)
    As = np.dot(PA,temp)
    Ps_initial = Ps
    xs_initial = xs[-1]
    Ezz[-1] = Ps + np.dot(np.reshape(xs[-1],(xs[-1].size,1)),np.reshape(xs[-1].transpose(),(1,xs[-1].size)))

    for i in np.arange(T-2,-1,-1):
        PA = np.dot(P_hat[i],A.transpose())
        temp = np.dot(A,PA) + W
        temp = np.linalg.inv(temp)
        As = np.dot(PA,temp)
        xs[i] = np.dot(As,xs_initial) + x_hat[i] - np.dot(As,np.dot(A,x_hat[i]))
        Ez1z[i] = np.dot(Ps,As.transpose()) + np.dot(np.reshape(xs[i+1],(xs[i+1].size,1)),np.reshape(xs[i].transpose(),(1,xs[i].size)))
        Ps = P_hat[i] + np.dot(As,np.dot(Ps,As.transpose())) - np.dot(PA,As.transpose())
        xs_initial = xs[i]
        Ezz[i] = Ps + np.dot(np.reshape(xs[i],(xs[i].size,1)),np.reshape(xs[i].transpose(),(1,xs[i].size)))

    return xs,Ez1z,Ezz

def isTiny(A):
    return (np.linalg.norm(A, 1) < 1e-10) or (any(np.diag(A) < 1e-10))

def logdet(A,use_chol=1):

    if use_chol:
        v = 2*np.sum(np.log(np.diag(np.linalg.cholesky(A).transpose())));
    else:
        P,L,U = sp.linalg.lu(A);
        du = np.diag(U);
        c = np.linalg.det(P)*np.prod(np.sign(du));
        v = np.log(c) + np.sum(np.log(np.abs(du)));

    return v
