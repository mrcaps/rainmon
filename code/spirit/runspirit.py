#!/usr/bin/python
#wrapper to run SPIRIT
#@author ishafer

import os, json, sys, optparse
#if importing wx on the fly is desirable
from numpy import *
from spirit import *
from pylab import *
sys.path.append(os.path.abspath("../"))
from preprocess import *
from analysis import *

#run an experiment with spirit, logging enabled
#minitial: initial number of principal components
def run_spirit(dm, minitial):
    sp = Spirit(dm.nattrs(), minitial)
    data = dm.get_data()
    print "Data shape sending to SPIRIT:", data.shape
    sp.run(data, True)
    reclog = sp.getreclog()

    return (data, reclog, sp)

#plot error as a function of number of initial principal components
#loc: output file
def error_vs_minitial(loc,dm,mmax):
    (pcs, errs, nworses) = vary_pcs(dm,mmax)
    
    MARKERSIZE = 15

    figure()
    plot(pcs, errs, 'b.-', markersize=MARKERSIZE)
    ylim(ymin=0)
    xlabel("Number of Principal Components")
    ylabel("R^2")
    twinx()
    plot(pcs, nworses, 'r.-', markersize=MARKERSIZE)
    ylim(ymin=0)
    ylabel("# Mean Superior")
    savefig(loc,format='png')
    show()

#vary the number of initial principal components for SPIRIT IPCA
def vary_pcs(dm,mmax):
    pcs = zeros((mmax))
    errs = zeros((mmax))
    nworses = zeros((mmax))
    for nrm in xrange(1,mmax+1):
        (data, reclog, sp) = run_spirit(dm, nrm)
        (err, worse) = recon_error_all(data, reclog)
        pcs[nrm-1] = nrm
        errs[nrm-1] = err
        nworses[nrm-1] = len(worse)

    print "It would have been better to store the mean for..."
    for wdx in worse:
        print "%4s %s" % (wdx, dm.attrname(wdx))

    return (pcs, errs, nworses)

#test effect of normalization
#loc: output file
#dm: datamatrix
def normalization_effect(loc,dm):
    NPCS = 25
    dm.print_stats()
    (pcs, errs, nworses) = vary_pcs(dm,NPCS)
    dm.transform_all()
    dm.print_stats()
    (pcs2, errs2, nworses2) = vary_pcs(dm,NPCS)

    MARKERSIZE = 15

    figure()
    plot(pcs, errs, 'b.-', markersize=MARKERSIZE)
    ylim(ymin=0,ymax=1)
    xlabel("Number of principal components")
    ylabel("R^2")
    plot(pcs, errs2, 'g.-', markersize=MARKERSIZE)
    legend(['unnormalized','normalized'],'lower right')
    show()

def plot_recon_error_all(data, reclog, dm, maxplots, wastransformed):
    matplotlib.rc("lines", linewidth=5)

    for i in xrange(min(maxplots, len(data[0]))):
        loc = os.path.join(tmpdir, "recon" + str(i) + ".png")
        xs = data[:,i]
        ys = reclog[:,i]
        if wastransformed:
            xs = dm.untransform(xs, i)
            ys = dm.untransform(ys, i)
        #to save data rather than plot it
        #numpy.savez(loc, xs=xs, ys=ys)
        #numpy.savetxt(loc,(xs,ys))
        plot_recon(loc, xs, ys, thetitle=dm.attrname(i), showlegend=False)

    print "Reconstruction error was: ", recon_error_all(data,reclog)

def plot_hvs_all(ylog, dm, maxplots):
    matplotlib.rc("lines", linewidth=5)

    for i in xrange(min(maxplots, ylog.shape[1])):
        loc = os.path.join(tmpdir, "hv" + str(i) + ".png")
        hv = ylog[:,i]
        figure()
        plot(hv, 'r-')
        title("Hidden variable " + str(i), fontsize="large")
        xlabel("Time Tick")
        ylabel("Value")
        savefig(loc,format='png')

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-o', action="store", help="Plot generation option")

    opts, args = parser.parse_args(sys.argv)

    cfg = getconfig()
    tmpdir = cfg["tmpdir"]
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)

    def load_data(tick, dotransform):
        dm = DataMatrix(cfg["externaldata"])
        dm.load()
        #interpolate and flatten to matrix
        # e.g. 300s = 5 minute ticks
        dm.flatten(tick)
        ##dm.print_metrics()
        #apply forward transformation to 0..1
        if dotransform:
            dm.transform_all()
        dm.print_stats()
        return dm

    gen = opts.o
    if gen == "sample-data":
        target = gettarget(cfg["datadir"], 0)
        data = readdat(target)
    elif gen == "recon-error-all":
        transformit = True
        dm = load_data(30, transformit)
        hiddenvars = 10
        #dm.removeattrs([1,5,9,13,14,17,21])\
        (data, reclog, sp) = run_spirit(dm, hiddenvars)
        plot_recon_error_all(data, reclog, dm, 30, transformit)
        hvlog = sp.gethvlog()
        plot_hvs_all(hvlog, dm, hiddenvars)
    elif gen == "normalization-effect":
        dm = load_data(300, False)
        normalization_effect(os.path.join(tmpdir,"normalizationeffect.png"),dm)
    elif gen == "error-vs-minitial":
        error_vs_minitial(os.path.join(tmpdir,"rcerr.png"),dm,8)