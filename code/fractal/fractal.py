#!/usr/bin/python
#Tools for fractal analysis on the dataset
#@author ishafer

import os, json, sys, optparse, subprocess
from numpy import *
from pylab import *
sys.path.append(os.path.abspath("../"))
from preprocess import *
from analysis import *

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-o', action="store", help="Data generation option")

    opts, args = parser.parse_args(sys.argv)

    cfg = getconfig()
    tmpdir = cfg["tmpdir"]
    mode = opts.o
    if mode == "dump":
    	dm = DataMatrix(cfg["externaldata"])
        dm.load()
        #interpolate and flatten to matrix
        # e.g. 300s = 5 minute ticks
        for (name,v) in dm.metrics.iteritems():
        	ts = v[0][0]
        	vs = v[0][1]
        	fd = open(os.path.join(tmpdir,name + ".datapoints"),"w")
        	for i in xrange(len(vs)):
        		fd.write("%f %f\n" % (ts[i], vs[i]))
        	fd.close()
    elif mode == "fdnq":
    	fdnqloc = cfg["fdnqloc2"]
    	cands = os.listdir(tmpdir)
    	for f in cands:
    		if f.endswith(".datapoints"):
    			fullpath = os.path.abspath(os.path.join(tmpdir, f))
    			cmdline = ["perl", os.path.join(fdnqloc, "fdnq.pl"), "-q0 -h", fullpath]
    			proc = subprocess.Popen(cmdline, cwd=fdnqloc, stdout=subprocess.PIPE)
    			result = proc.communicate()[0]
    			print f + "\n\t" + result[:-1]