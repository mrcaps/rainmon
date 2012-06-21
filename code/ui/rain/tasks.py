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

#Celery data worker backend
#@author ishafer

try:
    from celery.decorators import task
except:
    def task():
        def decorator(target):
            return target
        return decorator
import sys

IMPORTPATH = "../../"
if IMPORTPATH not in sys.path:
    sys.path.append(IMPORTPATH)
from pipeline import *
from rescache import *

def getconfig():
    fp = open("config.json")
    st = fp.read()
    fp.close()
    return json.loads(st)

#@param savename the name of the subdirectory save name
def getcachedir(savename):
    cfg = getconfig()
    cdir = os.path.join(cfg["tmpdir"][3:],"cache")    
    return os.path.join(cdir,savename)

@task()
def add(x, y):
    return str(x + y) + "was a test."

#@param outname the output directory name for the save cache
#@param machines the list of nodes to run the analysis over
#@param attributes the list of metrics to run the analysis over
#@param startt starting time for analysis
#@param endt ending time for analysis
#@param tstep optional step time to pass to backends that accept a step
#@param tsdbhost timeseries database host (overrides default in pipeline)
#@param tsdbport timeseries database port (overrides default in pipeline)
#@param skipstages a list of stages to skip (e.g. pipeline.KalmanStage)
@task()
def run_pipeline(outname, machines, attributes, startt, endt, \
    tstep=None, tsdbhost=None, tsdbport=None, skipstages=None):
    print ">>>Running pipeline on ", machines, attributes
    print ">>>In time range", startt, endt
    print ">>>Skipping stages", skipstages
    print ">>>Saving to", outname

    cdir = getcachedir(outname)
    try:
        os.makedirs(cdir)
    except:
        pass

    pipeline = get_default_pipeline()
    if skipstages != None:
        pipeline.set_skipstages(skipstages)
    input = {} 
    input['hosts'] = machines
    input['metrics'] = attributes
    input['start'] = startt #'2011/11/01-00:00:00'
    input['end'] = endt #'2011/11/01-23:30:00'
    if tsdbhost != None:
        input['tsdbhost'] = tsdbhost
    if tsdbport != None:
        input['tsdbport'] = tsdbport
    if tstep != None:
        input['tstep'] = tstep
    print "Starting with input", input

    dump = Cache(cdir)
    def statuswriter(txt):
        withnl = txt + "\n"
        sys.stdout.write(withnl)
        dump.printstatus(withnl)
    output = pipeline.run(input,statuscb=statuswriter)
    #print "Got output: ", output.keys()
    
    dump.write(output)
    
    print "Analysis Done"

    return "Done"

@task()
def get_savenames():
    root = getcachedir("")
    saves = []
    for d in os.listdir(root):
        abspath = os.path.join(root,d)
        if os.path.isdir(abspath):
            saves.append(d)
    return saves

@task()
def get_status(savename):
    cache = Cache(getcachedir(savename))
    return cache.getstatus()

@task()
def get_summary(savename):
    cache = Cache(getcachedir(savename))
    return cache.getsummary()

@task()
def get_file(savename,fname):
    cache = Cache(getcachedir(savename))
    return cache.load(fname)        

#get timeseries from the specified save name
@task()
def get_ts(savename, key, tmin, tmax):
    cache = Cache(getcachedir(savename))
    tsdata = cache.load(key)
    tstimes = cache.load("tsample")
    return zip(tstimes, tsdata)