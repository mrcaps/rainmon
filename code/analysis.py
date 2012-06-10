#!/usr/bin/python
#Result analysis functions/plots
#@author ishafer

import matplotlib
font = {"size": "16"}
matplotlib.rc("font", **font)

from pylab import *
WXVER_SET = True

#loc: place to save the plot
#actual: actual data
#recon: reconstruction
def plot_recon(
    loc, 
    actual, 
    recon,
    thetitle="Actual vs reconstruction", 
    showlegend=True):
    if not WXVER_SET:
        import wxversion
        wxversion.select('2.8')
        import wx
        wxverset = True

    figure()
    plot(actual, 'r-')
    plot(recon, 'b--')
    title(thetitle)
    if showlegend:
        legend(['actual','reconstructed'],'lower right')
    xlabel('Time Tick')
    ylabel('Value')
    savefig(loc,format='png')

#Get r^2 reconstruction error between two 1D vectors
# act: actual signal
# est: reconstruction
def recon_error(act,est):
    assert act.shape == est.shape
    ssr = 0 #residuals
    sst = 0 #total
    actbar = mean(act)
    for i in xrange(act.shape[0]):
        ssr += (act[i] - est[i])**2
        sst += (act[i] - actbar)**2
    if 0 == sst:
        v = 1.0-sst
    else:
        v = 1.0-ssr/sst
    
    if v < 0:
        print "Warning: negative r^2"
        return (0,True)
    else:
        return (v,False)

#Get overall reconstruction error between [timeticks]x[n_metrics] signals
# By taking geometric mean
#return (error, number_worse_than_mean)
def recon_error_all(act,est):
    assert act.shape == est.shape
    M = act.shape[1]
    #sum of logs of errors
    slnerr = 0
    worse = []
    errs = zeros((M))
    for i in xrange(M):
        (err, isworse) = recon_error(act[:,i],est[:,i])
        errs[i] = err
        slnerr += log(err)
        if isworse:
            worse.append(i)
    
    #transform back to geometric error
    geoerror = exp(slnerr/M)
    return (geoerror, worse, errs)