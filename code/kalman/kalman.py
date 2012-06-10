# kalman.py

"""
Note: We now use direct matrix inversion in the parameter estimation part of the code.
Replace the direct matrix inversion with the Woodbury Identity for the matrix inversion.

"""

import numpy as np
import scipy as sp
from scipy import linalg

class lds_model(object):
    def __init__(self, A,C,Q,R,mu0,Q0):
        self.A = A
        self.C = C
        self.R = R
        self.Q = Q
        self.mu0 = mu0
        self.Q0 = Q0

def learn_lds(model,X,T,H,step_size,maxIter=10,lookahead_flag=1):

    thresh = 2

    N,M = X.shape
    
    XHat = np.zeros((N,M))
    ZHat = np.zeros((N,H))
    ZHat[0:T],XHat[0:T],model = learn_lds_block(X[0:T],H,model,maxIter)
    z_temp,x_temp = ZHat[0:T],XHat[0:T]

    val = []
    
    i = T
    while (i < N):
        
        print i
        if (i+step_size) > N:
            index = N
        else:
            index = i+step_size

        cum_err,ind,z_hat,x_hat = compute_forward_cum_err(X[i:index],model,z_temp[-1],step_size,thresh)

        if ind == 0:
            z_hat[1] = np.mean(ZHat[i-T:i],0)
            x_hat[1] = np.mean(XHat[i-T:i],0)
            A = np.eye(H, H)
            C = np.eye(M, H)
            Q = np.eye(H, H)
            R = np.eye(M, M)
            mu0 = np.random.randn(1,H)
            Q0 = Q
            model = lds_model(A,C,Q,R,mu0,Q0)
            ind = 1

        if lookahead_flag == 0:
            ind  = step_size

        # T1 = 0
        # maxIter1 = 0
        # while ind == 0:
        #     pdb.set_trace()
        #     T1 = T+T1
        #     maxIter1 = maxIter1 + maxIter
        #     z_temp,x_temp,model = learn_lds_block(X[i-T1:i],H,model,maxIter1)
        #     cum_err,ind,z_hat,x_hat = compute_forward_cum_err(X[i:index],model,z_temp[-1],step_size,thresh)

        if (i+ind) > N:
            temp_val = N - i
            ZHat[i:] = z_hat[0:temp_val]
            XHat[i:] = x_hat[0:temp_val]
        else:
            ZHat[i:i+ind] = z_hat[0:ind]
            XHat[i:i+ind] = x_hat[0:ind]

        i = i + ind
        z_temp,x_temp,model = learn_lds_block(X[i-T:i],H,model,maxIter)

        if lookahead_flag:
            step_size = 10*ind
        
        val.append(ind)
    
    return ZHat,XHat,val

def learn_lds_block(X,H,model,maxIter=10):
    X_original = X
    N,M = X.shape

    CONV_BOUND = 1e-4
    LL = np.zeros((maxIter,1))

    ratio = 1
    diff = 1
    iter = 1
    oldlogli = -np.inf

    converged = 1

    while (converged):
        oldmodel = model
        [mu, V, P, logli] = forward(X, model)
        [Ez, Ezz, Ez1z] = backward(mu, V, P, model)
        model = MLE_lds(X, Ez, Ezz, Ez1z)
        logli = np.real(logli)
        LL[iter-1] = logli
        oldlogli = logli
        s = 'iteration = ' + str(iter) + ', logli = ' + str(logli)
        print(s)
        converge,decrease = em_converged(logli,oldlogli)
        converged = converge and (iter < maxIter)
        iter = iter + 1

    model = oldmodel
    XHat = estimate_observations(model,Ez)
    
    return Ez,XHat,model

def forward(X,model):

    N,M = X.shape
    H,H = (model.A).shape
    Ih = np.eye(H, H)

    mu = np.zeros((N,H))
    V = np.zeros((N,H,H))
    P = np.zeros((N,H,H))

    mu[0] = model.mu0
    V[0] = model.Q0
    logli = 0

    for i in np.arange(N):
        if (i == 0):
            KP = model.Q0
            mu[i] =  model.mu0
        else:
            P[i-1] = np.dot(model.A,np.dot(V[i-1],model.A.transpose())) + model.Q
            KP = P[i-1]
            mu[i] =  np.dot(model.A,mu[i-1])
        
        sigma_c = np.dot(model.C,np.dot(KP,model.C.transpose())) + model.R
        invSig = np.linalg.inv(sigma_c)

        K = np.dot(KP,np.dot((model.C).transpose(),invSig))
        u_c = np.dot(model.C,mu[i])
        delta = X[i] - u_c
        mu[i] = mu[i] + np.dot(K,delta)
        V[i] = np.dot((Ih - np.dot(K,model.C)),KP)
        posDef = np.dot(delta.transpose(),np.dot(invSig,delta/2))
        if (posDef < 0):
            print('det of not positive definite < 0')

        logli = logli - M/2*np.log(2*np.pi) + logdet(invSig)/2 - posDef

    return mu,V,P,logli

def backward(mu,V,P,model):

    N,M = mu.shape
    Ez = np.zeros((N,M))
    Ezz = np.zeros((N,M,M))
    Ez1z = np.zeros((N,M,M))
    Ez[-1] = mu[-1]
    Vhat = V[-1]
    Ezz[-1] = Vhat + np.outer(Ez[-1],Ez[-1])

    for i in np.arange((N-2),-1,-1):
        J = np.dot(np.dot(V[i],model.A.transpose()),np.linalg.inv(P[i]))
        Ez[i] = mu[i] + np.dot(J,(Ez[i+1] - np.dot(model.A,mu[i])))
        Ez1z[i] = np.dot(Vhat,J.transpose()) + np.outer(Ez[i+1],Ez[i])
        Vhat = V[i] + np.dot(J,np.dot((Vhat - P[i]),J.transpose()))
        Ezz[i] = Vhat + np.outer(Ez[i],Ez[i])

    return Ez,Ezz,Ez1z

def MLE_lds(X, Ez, Ezz, Ez1z,DiagQ0=1,DiagQ=1,DiagR=1):

    N,M = X.shape
    N,H = Ez.shape
    Sz1z = np.zeros((H, H))
    Szz = np.zeros((H, H))
    Sxz = np.zeros((M, H))

    for i in np.arange(N-1):
        Sz1z = Sz1z + Ez1z[i]

    for i in np.arange(N):
        Szz = Szz + Ezz[i]
        Sxz = Sxz + np.outer(X[i],Ez[i])

    SzzN = Szz - Ezz[-1]

    mu0 = Ez[0]
    Q0 = Ezz[0] - np.outer(Ez[0],Ez[0])
    if DiagQ0:
        Q0 = np.diag(np.diag(Q0))
    A = np.dot(Sz1z,np.linalg.inv(SzzN))
    tmp = np.dot(A,Sz1z.transpose())
    if DiagQ:
        Q = np.diag((np.diag(Szz)-np.diag(Ezz[0])-2*np.diag(tmp)+np.diag(np.dot(A,np.dot(SzzN,A.transpose()))))/(N-1))
    else:
        Q = (Szz - Ezz[0] - tmp - tmp.transpose() + np.dot(A,np.dot(SzzN,A.transpose())))/(N-1)
    C = np.dot(Sxz,np.linalg.inv(Szz))
    tmp = np.dot(C,Sxz.transpose())
    if DiagR:
        R = np.diag((np.diag(np.dot(X.transpose(),X))-2*np.diag(tmp)+np.diag(np.dot(C,np.dot(Szz,C.transpose()))))/N)
    else:
        R = (np.dot(X.transpose(),X) - tmp - tmp.transpose() + np.dot(C,np.dot(Szz,C.transpose())))/N

    model = lds_model(A,C,Q,R,mu0,Q0)
    return model

def estimate_observations(model,Z):

    N,M = Z.shape
    H,M = (model.C).shape
    X = np.zeros((N,H))

    for i in np.arange(N):
        X[i] = np.dot(model.C,Z[i])

    return X

def predict_observations(model,Z0,step_size):
    H,M = (model.C).shape
    
    Z = np.zeros((step_size,M))
    X = np.zeros((step_size,H))

    Z[0,:] = np.dot(model.A,Z0)
    X[0,:] = np.dot(model.C,Z[0])

    for i in np.arange(1,step_size):
        Z[i,:] = np.dot(model.A,Z[i-1])
        X[i,:] = np.dot(model.C,Z[i])

    return Z,X

def logdet(A,use_chol=0):
    if use_chol:
        v = 2*np.sum(np.log(np.diag(np.linalg.cholesky(A).transpose())))
    else:
        P,L,U = sp.linalg.lu(A)
        du = np.diag(U)
        c = np.linalg.det(P)*np.prod(np.sign(du))
        v = np.log(c) + np.sum(np.log(np.abs(du)))

    return v

def is_tiny(A):
    return (np.linalg.norm(A, 1) < 1e-10) or (np.any((np.diag(A)) < 1e-10))

def em_converged(logli,oldlogli,threshold=1e-4,check_increased=1):

    eps = 1e-16
    converged = 0;
    decrease = 0;

    if check_increased:
        if ((logli - oldlogli) < -1e-3):
            print '******likelihood decreased from '+str(oldlogli)+' to '+str(logli)+'\n'
            decrease = 1;
            converged = 0;
            return converged, decrease

    
    delta_logli = np.abs(logli - oldlogli);
    avg_logli = (np.abs(logli) + np.abs(oldlogli) + eps)/2;
    if ((delta_logli/avg_logli) < threshold):
        converged = 1

    return converged, decrease


def compute_forward_cum_err(X,model,z_temp,step_size,thresh):

    N,dim = X.shape
    
    if step_size > N:
        step_size = N
    
    z_hat,x_hat = predict_observations(model,z_temp,step_size)
    tmp = np.max(np.abs(X),0)
    tmp[tmp==0] = 1
    err = (x_hat - X)/tmp
    cum_err = np.cumsum(np.sqrt(np.mean(err**2,1)))
    ind = np.argmin(cum_err <= thresh)
        
    if np.max(cum_err) < thresh:
        ind = len(cum_err)

    if np.min(cum_err) > thresh:
        ind = 0

    return cum_err,ind,z_hat,x_hat