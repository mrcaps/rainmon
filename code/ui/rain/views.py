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

#Webserver views for web UI
#@author ishafer

import time

from django.template import Context, loader
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

import random, json
import rain.tasks as tasks

def index(request):
    t = loader.get_template("index.html")
    c = Context({'cs': time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime(time.time()-60*60)),
                 'ce': time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime()),
                 'metric': 'cpu_user',
                 'hostid': 'cloud1'})
    return HttpResponse(t.render(c))

def fakedata(tmin,tmax):
    pts = []
    NPTS = 500
    for i in xrange(NPTS):
        t = float(i)/float(NPTS)*(tmax-tmin)+tmin
        pts.append([t, random.random()])
    return pts

def downsample(pts,minlen):
    ptslen = len(pts)
    if ptslen > minlen:
        return pts[::int(ptslen/minlen)]
    else:
        return pts

DOWNSAMPLEPTS = 1000

def data(request):
    savename = request.GET['savename']
    node = request.GET['node']
    metric = request.GET['metric']
    tmin = float(request.GET['tmin'])
    tmax = float(request.GET['tmax'])
    pts = tasks.get_ts(savename, metric, tmin, tmax)
    #return a max of 1000 points
    pts = downsample(pts,DOWNSAMPLEPTS)
    return HttpResponse(json.dumps({"dta": pts}).replace("NaN","\"NaN\""))

def analyze(request):
    outname = str(request.GET['outname'])
    machines = json.loads(request.GET['machines'])
    attributes = json.loads(request.GET['attributes'])
    tmin = json.loads(request.GET['tmin']).encode('ascii', 'ignore')
    tmax = json.loads(request.GET['tmax']).encode('ascii', 'ignore')
    sourcename = None
    if 'sourcename' in request.GET:
        sourcename = str(request.GET['sourcename'])
    tsdbhost = None
    if 'tsdbhost' in request.GET:
        tsdbhost = str(request.GET['tsdbhost'])
    tsdbport = None
    if 'tsdbport' in request.GET:
        tsdbport = str(request.GET['tsdbport'])
    tstep = None
    if 'tstep' in request.GET:
        tstep = float(request.GET['tstep'])

    if request.GET['cloudifyNames'] and json.loads(request.GET['cloudifyNames']):
        machines = ["cloud" + str(int(s)) for s in machines]
    else:
        machines = [m.encode('ascii', 'ignore') for m in machines]
    attributes = [u.encode('ascii', 'ignore') for u in attributes]
    #print "Running on ", machines, attributes

    if 'skipstages' in request.GET:
        skipstages = json.loads(request.GET['skipstages'])
        skipstages = [s.encode('ascii','ignore') for s in skipstages]
    else:
        skipstages = ["pipeline.KalmanStage","pipeline.DrawStage"]

    result = tasks.run_pipeline.delay(
        outname=outname, machines=machines, attributes=attributes, startt=tmin, endt=tmax, \
        tstep=tstep, sourcename=sourcename, tsdbhost=tsdbhost, tsdbport=tsdbport, skipstages=skipstages)
    #don't block on response
    #print result.get()

    return HttpResponse(json.dumps({"message": "running"}))

def getsavenames(request):
    t = tasks.get_savenames.delay()
    result = t.get()
    return HttpResponse(json.dumps(result))    

def getstatus(request):
    savename = request.GET['savename']
    t = tasks.get_status.delay(savename)
    result = t.get()
    return HttpResponse(json.dumps(result))

def getsummary(request):
    savename = request.GET['savename']
    t = tasks.get_summary.delay(savename)
    result = t.get()
    result["tsample"] = downsample(result["tsample"],DOWNSAMPLEPTS)
    #print "Got results map", result
    return HttpResponse(json.dumps(result))

def getprojection(request):
    savename = request.GET['savename']
    t = tasks.get_file.delay(savename, "projection")
    result = t.get()
    return HttpResponse(json.dumps(result))

def getheatmap(request):
    savename = request.GET['savename']
    t = tasks.get_file.delay(savename, "heatmap")
    result = t.get()
    return HttpResponse(json.dumps(result))