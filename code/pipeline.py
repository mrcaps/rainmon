#!/usr/bin/python

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

#########################################################################
# Author: Kai Ren
# Created Time: 2011-11-22 14:45:29
# File Name: ./preprocess.py
# Description: 
#########################################################################
import cypress
import spirit
import kalman
import string
import numpy
import urllib
import pylab
import matplotlib.pyplot as plt
import json
import hashlib
import os
import sys
import cPickle
import time
import math
import os.path

from preprocess import transforms, getmetrics
from analysis import *
from lib import deep_eq

def getconfig():
    fp = open("config.json")
    st = fp.read()
    fp.close()
    return json.loads(st)

class Pipeline:
    '''
    A batch analysis pipeline
    '''
    def  __init__(self,skipstages=[]):
        self.stages = []
        self.skipstages = skipstages

    def resize(self, num):
        '''
        @param num: how many stages should this pipeline now have?
        '''
        self.stages = [None] * num

    def set_skipstages(self,skipstages):
        '''
        @param skipstages: list of stages to skip when executing pipeline
        '''
        self.skipstages = skipstages

    def set_stage(self, stage_no, stage_func):
        '''
        @param stage_no: the index of the stage to set
        @param stage_func: which stage to replace it with
        '''
        if stage_no < len(self.stages):
            self.stages[stage_no] = stage_func

    def append_stage(self, stage_func):
        '''
        @param stage_func: a stage to add to the end of the pipeline
        '''
        self.stages.append(stage_func)

    def get_stages(self, cname):
        '''
        Get stages by class name
        '''
        match = []
        for stage in self.stages:
            if cname in stage.__class__.__name__:
                match.append(stage)
        return match

    def run(self, input, statuscb=None):
        '''
        @param input: dictionary of inputs (see individual stage run() documentation for required keys)
        @param statuscb: callback(string) for status messages
        '''
        output = None

        if statuscb == None:
            statuscb = lambda s: sys.stdout.write(s + "\n")
        
        for stage in self.stages:
            if any([stage.__class__.__name__ in s for s in self.skipstages]):
                statuscb("Skipping stage %s" % (stage))
            else:
                statuscb("Running stage %s" % (stage))
                output = stage.run(input)
                input = output
        statuscb("Analysis Complete")
        return output


class OpenTSDBCrawlStage:
    '''
    Obtain timeseries data from an OpenTSDB-format-compatible data source
    '''
    def __init__(self, host, port):
        '''
        @param hostname: (without http), e.g. 127.1.1.1
        @param port: timeseries database port (4242 is OpenTSDB default)
        '''
        self._host = str(host)
        self._port = str(port)

    def get_query(self, metric, hosts, start, end):
        '''
        Obtain the URL for an OpenTSDB query
        @param metric: e.g. iostat.disk.write_requests
        @param hosts: list of host strings
        @param start: start time (as %Y/%m/%d-%H:%M:%S)
        @param end: end time (as %Y/%m/%d-%H:%M:%S)
        '''
        tagpos = metric.find(',')
        if tagpos >= 0:
            tags = metric[tagpos:].replace('.', '=')
            metric = metric[:tagpos]
        else:
            tags = ""
        isRate = True
        if metric.find('memoinfo') >= 0:
            isRate = False
        if isRate:
            url = "http://%s:%s/q?start=%s&end=%s&m=sum:rate:%s{host=%s%s}&ascii"%\
                (self._host, self._port, start, end, metric, hosts, tags)
        else:
            url = "http://%s:%s/q?start=%s&end=%s&m=sum:%s{host=%s%s}&ascii"%\
                (self._host, self._port, start, end, metric, hosts, tags)
        return url

    def download(self, url, start, end):
        '''
        Obtain data from OpenTSDB
        @param url: see get_query
        @param start: start time (as %Y/%m/%d-%H:%M:%S)
        @param end: end time (as %Y/%m/%d-%H:%M:%S)
        '''
        start_tuple = time.strptime(start, "%Y/%m/%d-%H:%M:%S")
        start_time = int(time.mktime(start_tuple))
        end_tuple = time.strptime(end, "%Y/%m/%d-%H:%M:%S")
        end_time = int(time.mktime(end_tuple))
        hosts = {}
        sys.stderr.write("%d %d\n"%(start_time, end_time))
        f = urllib.urlopen(url)
        try:
            for l in f:
                items = l.split()
                name = ""
                for i in range(3, min(5, len(items))):
                    if items[i].startswith('host'):
                        name = items[i][5:]
                if not name in hosts:
                    hosts[name] = [[], []]
                ts = int(items[1])
                if ts >= start_time and ts <= end_time:
                    hosts[name][0].append(int(items[1]))
                    val = float(items[2])
                    if val < 0 or math.isnan(val):
                        val = 0
                    hosts[name][1].append(val)
        except:
            print "parse error: %s"%(url)
        f.close()
        return hosts

    def run(self, input):
        '''
        Run an OpenTSDB crawl.
        Required input keys:
        metrics: a list of metrics
        hosts: a list of objects (hosts) to get data from

        Optional input keys:
        tsdbhost: timeseries database host to override constructor
        tsdbport: timeseries database port to override constructor
        tstep: time step in seconds for backends that understand it

        Output keys:
        data
        ts_names
        '''
        if "tsdbhost" in input:
            host = input["tsdbhost"]
            if host != None:
                self._host = str(host)
        if "tsdbport" in input:
            port = input["tsdbport"]
            if port != None:
                self._port = str(port)
        hosts = string.join(input['hosts'], '|')
        metrics = input['metrics']
        start = input['start']
        end = input['end']
        nmet = len(metrics)
        nout = len(input['hosts']) * nmet
        output = {}
        output['ts_names'] = [''] * nout 
        output['metrics'] = metrics
        output['hosts'] = input['hosts']
        output['data'] = [[]] * nout
        if "tstep" in input:
            output["tstep"] = input["tstep"]
        mi = 0
        for metric in metrics:
            url = self.get_query(metric, hosts, start, end)
            #tstep currently only for backends that accept tstep query param
            if "tstep" in input and input["tstep"] != None:
                url += "&tstep=" + str(input["tstep"])
            print url
            data = self.download(url, start, end)
            hi = 0
            for host in input['hosts']:
                if host in data:
                    output['data'][hi * nmet + mi] = data[host]
                else:
                    output['data'][hi * nmet + mi] = None 
                output['ts_names'][hi * nmet + mi] = '%s.%s'%(host, metric)
                hi += 1
            mi += 1
        return output

class CachingCrawlStage:
    def __init__(self, root, host, port):
        '''
        @param root: the root directory to place tsdb caches in
        @param host: tsdb host to query
        @param port: port of tsdb to query
        '''
        self.root = root
        try:
            os.makedirs(root)
        except os.error:
            pass
        self.crawl = OpenTSDBCrawlStage(host, port)

    def run(self, input):
        '''
        Run the crawler, obtaining data from a cache if possible.
        Input/output keys are the same as OpenTSDBCrawlStage
        '''
        hascache = False

        #look for alternate caches by md5 terminator
        inputser = cPickle.dumps(input)
        hasher = hashlib.md5()
        hasher.update(inputser)
        inputhash = hasher.hexdigest()

        subdir = os.path.join(self.root, inputhash)
        cname = os.path.join(subdir, "input.pkl")
        dname = os.path.join(subdir, "tsdbcache.pkl")
        
        #do a crawl and write out input
        if not os.path.exists(cname):
            print "Cache >> Building Cache"
            try:
                os.makedirs(subdir)
            except:
                pass
            result = self.crawl.run(input)
            print "Cache >> got crawl; saving..."
            with open(dname,"wb") as fp:
                cPickle.dump(result, fp)
            
            with open(cname,"wb") as fp:
                cPickle.dump(input, fp)
        else:
            print "Cache >> Using Cached Results"
            with open(dname,"rb") as fp:
                result = cPickle.load(fp)
        
        return result

class ResampleStage:
    '''
    Resample input data to a consistent sample tick
    '''
    def __init__(self, step=20):
        '''
        @param step: timestep for resampling (in seconds)
        '''
        self.step = step
        pass

    def run(self, input):
        '''
        Required input keys:
        data, ts_names
        '''
        #take step input from the pipeline if available
        if "tstep" in input and input["tstep"] != None:
            self.step = int(float(input["tstep"]))
        mint = float("inf")
        maxt = float("-inf")
        for data in input['data']:
            if data is not None and len(data[0]) > 0:
                (ts, vs) = data
                mint = min(mint, ts[0])
                maxt = max(maxt, ts[len(ts)-1])
        
        print "Sampling from ", mint, maxt, self.step
        tsample = numpy.arange(mint, maxt, self.step)

        output_ts = []
        tsnames = []
        for ddx in xrange(len(input['data'])):
            data = input["data"][ddx]
            if data is not None and len(data[0]) > 0:
                (ts, vs) = data
                output_ts.append(numpy.interp(tsample, ts, vs))
                tsnames.append(input['ts_names'][ddx])
            #omit streams with errors obtaining data
            #else:
            #    output_ts.append(numpy.array([0] * len(tsample)))
        
        output = {}
        output['ts_names'] = tsnames
        output['mint'] = mint
        output['maxt'] = maxt
        output['step'] = self.step
        output['tsample'] = tsample
        output['data'] = output_ts
        output['hosts'] = input['hosts']

        return output

class CypressStage:
    def __init__(self, skipstage=False, add_lofhof=True):
        '''
        @param skipstage: should we skip this stage (for comparison with other methods)?
        @param add_lofhof: should LoF and residuals be added for smooth output?
        '''
        self.add_lofhof = add_lofhof
        self.skipstage = skipstage
        self.cyp = cypress.Cypress()

    def run(self, input):
        '''
        Required input keys:
        data, step
        '''
        step = input['step']
        output_ts = []
        for ts in input['data']:
            if self.skipstage:
                output_ts.append([ts,0,0])
            else:
                if self.add_lofhof:
                    output_ts.append(self.cyp.transform(ts, step))
                else:
                    output_ts.append(self.cyp.transform_retlof(ts, step))
            output_ts[-1].append(ts)
        output = {}
        output['mint'] = input['mint']
        output['maxt'] = input['maxt']
        output['step'] = input['step']
        output['tsample'] = input['tsample']
        output['ts_names'] = input['ts_names']
        output['data'] = output_ts
        output['hosts'] = input['hosts']
        return output

class TrimStage:
    '''
    Trim data mid-pipeline to avoid rebuilding cache for smaller output
    '''
    def __init__(self):
        self.trimhosts = False
        self.remtses = False
        self.remzero = False
    
    def sethosts(self, hosts):
        '''
        Set the maximum number of hosts to show
        '''
        self.trimhosts = hosts

    def setrem(self, tses):
        '''
        Set the indices of timeseries to remove
        '''
        self.remtses = tses
    
    def run(self, input):
        nmet = len(input["metrics"])
        output = input
        
        if self.trimhosts:
            trim = self.trimhosts * nmet
            output["ts_names"] = output["ts_names"][:trim]
            output["data"] = output["data"][:trim]
        if self.remtses:
            for ts in self.remtses:
                del output["ts_names"][ts]
                del output["data"][ts]

        #print "len", len(output["data"][0][0])

        return output

class NormalizeStage:
    def __init__(self, normalize, previous=None):
        '''
        @param normalize: should this normalize or un-normalize?
        @param previous: a previous NormalizeStage to be used for looking up stored transforms
        '''
        self.fwd = normalize
        self.prev = previous
        #transforms used by this stage
        self.used = dict()

    def get_transform(self, name):
        if self.prev is not None:
            #use the transform from the previous NormalizeStage if it exists
            if name in self.prev.used:
                return self.prev.used[name]

        trimsfx = ".None"
        if name.endswith(trimsfx):
            name = name[:-len(trimsfx)]
        #remove the machine name for table lookup
        name = name[name.find(".")+1:]
        if name in transforms:
            xf = transforms[name]
        else:
            print "No transform found for metric " + name
            xf = transforms["None"]
        self.used[name] = xf
        return xf

    def run(self, input):
        '''
        Required input keys:
        ts_names
        data

        Optional input keys:
        reconlog

        Output keys:
        xforms
        '''
        assert ("ts_names" in input), "NormalizeStage needs timeseries names"
        assert ("data" in input), "NormalizeStage needs data to transform"

        xforms = []
        for tsname in input["ts_names"]:
            xforms.append(self.get_transform(tsname))

        output = input
        output["xforms"] = xforms

        for i in xrange(len(output["data"])):
            #for now, only transform the smooth component
            idata = numpy.array(output["data"][i][0])
            if self.fwd:
                norm = xforms[i].apply(idata)
                #print "min/max of normalized %s: %f, %f" % \
                #    (input["ts_names"][i], min(norm), max(norm))
            else:
                norm = xforms[i].unapply(idata)

            output["data"][i][0] = norm
        
        #transform the reconstructions if they exist
        if "reconlog" in output:
            rlog = output["reconlog"]
            for i in xrange(rlog.shape[1]):
                if self.fwd:
                    rlog[:,i] = xforms[i].apply(rlog[:,i])
                else:
                    rlog[:,i] = xforms[i].unapply(rlog[:,i])

        return output

class CompressionStage:
    def __init__(self, outdir):
        self.outdir = outdir

    def run(self, input):
        '''
        Required input keys:
        maxhvs
        projection
        hvlog
        '''
        assert ("maxhvs" in input), "CompressionStage needs to know how many hvs to save"
        assert ("projection" in input), "CompressionStage requires PCA projection"
        assert ("hvlog" in input), "CompressionStage requires hidden variables"
        assert ("data" in input), "CompressionStage requires data from decomposition"

        saveargs = dict()

        maxhvs = input["maxhvs"]
        saveargs["maxhvs"] = maxhvs
        saveargs["proj"] = input["projection"][:maxhvs,:]
        saveargs["hvs"] = input["hvlog"][:maxhvs,:]

        spikes = []
        for ts in input["data"]:
            spikes.append(ts[1])
        spikes = np.array(spikes)
        saveargs["spikes"] = spikes

        #save transforms
        if "xforms" in input:
            saveargs["xforms"] = input["xforms"]
        if "center" in input:
            saveargs["center"] = input["center"]

        np.savez_compressed(os.path.join(self.outdir, "compressed"), **saveargs)

        return input

class HeatmapStage:
    def __init__(self):
        pass

    def run(self, input):
        '''
        Required input keys:
        data
        hosts
        tsnames
        '''
        assert ("data" in input), "HeatmapStage needs data to save"
        assert ("hosts" in input), "HeatmapStage must know hosts"
        assert ("ts_names" in input), "HeatmapStage must have list of timeseries names"

        data = input["data"]
        hosts = input["hosts"]
        tsnames = input["ts_names"]
        output = input

        output["heatmap"] = numpy.zeros((len(hosts),len(data[0][0])))
        for i in xrange(len(tsnames)):
            tsn = tsnames[i]
            hostdx = -1
            for j in xrange(len(hosts)):
                #left unrolled since this might need to change in the future
                if tsn.split(".")[0] == hosts[j]:
                    hostdx = j
                    break
            if hostdx == -1:
                print "Error: no known host for ", tsn
            output["heatmap"][hostdx,:] += data[i][0]**2

        return output

#Run SPIRIT on input["data"]
class SpiritStage:
    def __init__(self, ispca=True,thresh=0.05,startm=3,ebounds=(0.9995, 1),vlambda=0.99,pcafixk=False):
        self.ispca = ispca
        self.thresh = thresh
        self.startm = startm
        self.ebounds = ebounds
        self.vlambda = vlambda
        self.pcafixk = pcafixk

    def run(self, input):
        data = input["data"]
        #smoothed data from cypress
        smoothds = []
        for dtas in data:
            smoothds.append(dtas[0])
        dmat = numpy.array(smoothds)

        if self.ispca:
            #lower -> retain more energy
            alg = spirit.PCA(self.thresh)
            if self.pcafixk:
                alg.setfixk(self.pcafixk)
        else:
            alg = spirit.Spirit(dmat.shape[0], self.startm, self.ebounds, self.vlambda)
        alg.run(dmat.T, True)

        output = input
        #time history of hidden variables
        output["hvlog"] = alg.gethvlog().T
        #time history of SPIRIT reconstructions
        output["reconlog"] = alg.getreclog()
        #final SPIRIT projection matrix
        output["projection"] = alg.W
        #number of hidden variables at each time tick
        mlog = alg.getmlog()
        output["mlog"] = mlog
        #maximum number of hidden variables
        output["maxhvs"] = int(max(mlog))
        #minimum number of hidden variables
        output["minhvs"] = int(min(mlog))
        if alg.getcenter() != None:
            output["center"] = alg.getcenter()

        return input

# Run Kalman on Spirit Data
class KalmanStage:
    def __init__(self,step_size=10,lookahead_flag=1):
        self.step_size = step_size
        # the flag with controls adaptive lookahead. Set it to "0" for fixed lookahead.
        # the fixed lookahead is now controlled by step_size
        self.lookahead_flag = lookahead_flag

    def run(self,input):
        data = input["hvlog"]
        max_ind = numpy.max(input["mlog"])
        data = data[0:max_ind,:]
        data = data.transpose()
        N,M = data.shape
        H = numpy.max(numpy.array([2,numpy.ceil(M/3)]))
        
        T = 50
        maxIter = 20

        A = numpy.eye(H, H)
        C = numpy.eye(M, H)
        Q = numpy.eye(H, H)
        R = numpy.eye(M, M)
        mu0 = numpy.random.randn(1,H)
        Q0 = Q
        model = kalman.lds_model(A,C,Q,R,mu0,Q0)

        z_hat,y_hat,ind = kalman.learn_lds(model,data,T,H,self.step_size,maxIter,self.lookahead_flag)

        output = input
        output["predict"] = y_hat.transpose()
        output["smooth"] = z_hat.transpose()
        output["ind"] = np.array(ind)

        return input

class DrawStage:
    def __init__(self, outdir, fixymax):
        self.outdir = outdir
        self.fixymax = fixymax

    def run(self, input):
        outdir = self.outdir
        tsample = input['tsample']
        for i in range(len(input['data'])):
            ts = input['data'][i]
            pylab.clf()
            pylab.subplots_adjust(hspace=.7)
            pylab.subplot(4,1,1)
            pylab.title("original")
            pylab.plot(tsample, ts[3], 'r-')
            ymin, ymax = pylab.ylim()
            pylab.subplot(4,1,2)
            pylab.title("low pass + reconstruction")
            pylab.plot(tsample, ts[0], 'b-')
            if "reconlog" in input:
                reconlogi = input["reconlog"][:,i]
                pylab.plot(tsample, reconlogi, 'k--')
            if self.fixymax:
                pylab.ylim((ymin, ymax))
            pylab.subplot(4,1,3)
            pylab.title("spiky")
            pylab.plot(tsample, ts[1], 'g-')
            ymin, ymax = pylab.ylim()
            pylab.subplot(4,1,4)
            pylab.title("residual")
            pylab.plot(tsample, ts[2], 'g-')
            if self.fixymax:
                pylab.ylim((ymin, ymax))

            pylab.savefig(os.path.join(outdir, "test.%s.png"%(input['ts_names'][i])))
        #dump hidden variables if available
        if "hvlog" in input:
            hvs = input["hvlog"]
            hvsplot = len(hvs)
            if "maxhvs" in input:
                hvsplot = input["maxhvs"]
            for i in xrange(hvsplot):
                hv = hvs[i]
                pylab.clf()
                pylab.title("Hidden variable " + str(i))
                pylab.plot(hv, "r-")
                pylab.savefig(os.path.join(outdir, "hv.%d.png" % i))

        #dump number of hidden variables
        if "mlog" in input:
            pylab.clf()
            pylab.title("Number of hidden variables vs time")
            pylab.plot(input["mlog"], "r-")
            pylab.savefig(os.path.join(outdir, "hv.count.png"))            

        # dump kalman predictions of spirit hidden variables if available
        if "predict" in input:
            hvs_predict = input["predict"]
            hvs = input["hvlog"]
            max_ind = numpy.max(input["mlog"])
            mse = numpy.mean((hvs[0:max_ind,:]-hvs_predict)**2,0)
            pylab.clf()
            pylab.title("Kalman Filter Mean Squared Prediction Error ")
            pylab.subplot(111)
            pylab.plot(mse,'r')
            pylab.xlim(0,mse.size)
            pylab.savefig(os.path.join(outdir, "kalman_mse.png"))
            pylab.clf()
            pylab.title("# of Prediction Samples")
            pylab.subplot(111)
            pylab.plot(input["ind"],'r')
            pylab.xlim(0,input["ind"].size)
            pylab.savefig(os.path.join(outdir, "kalman_predict_samples.png"))
            print np.mean(input["ind"]), np.std(input["ind"])

            for i in xrange(len(hvs_predict)):
                hv = hvs[i]
                hv_predict = hvs_predict[i]
                pylab.clf()
                pylab.title("Predicted hidden variable " + str(i))
                pylab.subplot(111)
                p1 = pylab.plot(hv,'r-')
                p2 = pylab.plot(hv_predict,'b--')
                pylab.xlim(0,hv.size)
                pylab.legend(('Spirit Coefficients','Predicted Coefficients'))
                pylab.savefig(os.path.join(outdir, "predict_hv_%d.png" % i))
                
        return input

#compute reconstruction error
class ErrorStage():
    #addspikes: should spikes be added back in when calculating reconstruction error?
    def __init__(self,addspikes=True):
        self.addspikes = addspikes

    def run(self, input):
        print "Calculating error"
        results = input["data"]
        recon = input["reconlog"]

        original = zeros(recon.shape)
        lowpass = zeros(recon.shape)
        for m in xrange(recon.shape[1]):
            #difference from low pass
            lowpass[:,m] = results[m][0]
            #difference from original
            original[:,m] = results[m][3]
            #add spikes to reconstruction if specified.
            if self.addspikes:
                recon[:,m] += results[m][1]

        output = input
        output["error"] = recon_error_all(original, recon)

        return output

globalcfg = getconfig()
TSDBHOST = globalcfg["tsdbhost"]
TSDBPORT = globalcfg["tsdbport"]

def get_default_pipeline():
    cfg = getconfig()
    tmpdir = cfg["tmpdir"][3:]
    #crawler = OpenTSDBCrawlStage(TSDBHOST,TSDBPORT)
    crawler = CachingCrawlStage(os.path.join(tmpdir,"tsdb"),TSDBHOST,TSDBPORT)
    #trim = TrimStage()
    resample = ResampleStage(600)
    cypress = CypressStage()
    spirit = SpiritStage(ispca=False,thresh=0.01,ebounds=(0,1.1),startm=6)
    kalman = KalmanStage()
    normalize = NormalizeStage(True)
    denormalize = NormalizeStage(False)
    draw = DrawStage(tmpdir, False)
    errorcalc = ErrorStage()
    heatmap = HeatmapStage()
    compress = CompressionStage(tmpdir)
    pipeline = Pipeline()
    pipeline.append_stage(crawler)
    #pipeline.append_stage(trim)
    pipeline.append_stage(resample)
    pipeline.append_stage(cypress)
    pipeline.append_stage(normalize)
    pipeline.append_stage(spirit)
    pipeline.append_stage(heatmap)
    pipeline.append_stage(kalman)
    pipeline.append_stage(denormalize)
    #pipeline.append_stage(errorcalc)
    #pipeline.append_stage(draw)
    #pipeline.append_stage(compress)
    return pipeline

if __name__ == '__main__':
    pipeline = get_default_pipeline()
    input = {} 
    input['hosts'] = []
    for i in range(1, 65):
        input['hosts'].append('cloud%d'%(i))

    input['start'] = '2011/11/22-15:00:00'
    input['end'] = '2011/11/24-23:45:00'

    """
    metrics = ['iostat.disk.read_requests',
               'iostat.disk.write_requests',
               'iostat.disk.write_sectors',
               'proc.meminfo.buffers',
               'proc.meminfo.cached',
               'proc.stat.cpu,type.system',
               'proc.stat.cpu,type.user',
               'proc.stat.cpu,type.iowait',
               'proc.stat.cpu,type.nice',
               'proc.net.bytes,direction.in',
               'proc.net.bytes,direction.out',
               'proc.net.packets,direction.in',
               'proc.net.packets,direction.out',
               'proc.stat.intr'
               ]
    """

    """
    metrics = ['iostat.disk.read_requests',
               'iostat.disk.write_requests',
               'proc.meminfo.buffers',
               'proc.meminfo.cached',
               'proc.stat.cpu,type.system',
               'proc.stat.cpu,type.user',
               'proc.stat.cpu,type.iowait',
               'proc.net.bytes,direction.in',
               'proc.net.bytes,direction.out',
               'proc.net.packets,direction.in',
               'proc.net.packets,direction.out'
               ]
    """

    metrics = ['iostat.disk.read_requests',
               'iostat.disk.write_requests',
                ]

    input['metrics'] = metrics
    pipeline.run(input)
    
    # input['metrics'] = ['']
    # for metric in metrics:
    #     input['metrics'][0] = metric
    #     pipeline.run(input)
