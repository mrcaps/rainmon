#!/usr/bin/python
#preprocess OpenCloud data
#@author ishafer

import os, json, sys, optparse
from pylab import *
sys.path.append(os.path.abspath("../../data"))
sys.path.append(os.path.abspath("../data"))
from read_data import *

def getconfig():
    fp = open("../config.json")
    st = fp.read()
    fp.close()
    return json.loads(st)

#get a data file from _datadir_ with entry index _eidx_
def gettarget(datadir, eidx):
    rawfiles = os.listdir(datadir)
    files = []
    for file in rawfiles:
        if file[-3:] == "dat":
            files.append(file)
    print files
    target = os.path.join(datadir, files[eidx])
    return target

def readdat(fname):
    return genfromtxt(fname)

#flatten a map of 
# name => 1d vector
#to 2d matrix and return the
#tstep: time tick length for interpolation
def flattenmetrics(dct, tstep):
    ks = dct.keys()

    #first pass: find minimum/maximum time
    mint = float("inf")
    maxt = float("-inf")
    for metric in ks:
        (ts, vs) = dct[metric][0]
        mint = min(mint, ts[0])
        maxt = max(maxt, ts[len(ts)-1])
    tsample = arange(mint,maxt,tstep)
    
    #do interpolation
    mnames = []
    vals = zeros((len(ks), len(tsample)))
    rn = 0
    #print "Time deltas:"
    for metric in ks:
        mnames.append(metric)
        (ts, vs) = dct[metric][0]
        #print metric, numpy.diff(ts[:10])
        vals[rn,:] = numpy.interp(tsample, ts, vs)
        rn += 1
    
    return (mnames, vals, tsample)

class Transform:
    def __init__(self):
        self.hi = 0
        pass
    #apply the transformation function
    def apply(self,v):
        return v
    #inverse of the transformation function
    def unapply(self,v):
        return v
    #name of this transform
    def getname(self):
        return "Null"

class NormalTransform(Transform):
    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi
    def apply(self,v):
        return (v-self.lo)/(self.hi - self.lo)
    def unapply(self,v):
        return v*(self.hi-self.lo)+self.lo
    def getname(self):
        return "Linear"

class LogTransform(Transform):
    def __init__(self, lo, hi):
        assert lo >= 0
        self.lo = lo
        self.hi = hi
        self.loghi = log(hi)
    def apply(self,v):
        #transform x to be 
        return log(v-self.lo+1)/self.loghi
    def unapply(self,v):
        return exp(v*self.loghi)+self.lo-1
    def getname(self):
        return "Log"

#normalize in 0 to hi
class LinearNormalize(Transform):
    def __init__(self, lo, hi):
        self.hi = 5
        self.maxvpre = None
        self.minvpre = None
    def apply(self, v):
        self.maxvpre = max(v)
        self.minvpre = min(v)
        return (v-self.minvpre)/(self.maxvpre-self.minvpre)*self.hi
    def unapply(self,v):
        if self.maxvpre is None:
            print "Must normalize in the forward direction before reversing!"
        return (v/self.hi)*(self.maxvpre-self.minvpre)+self.minvpre
    def getname(self):
        return "LinearNorm"

#a few particularly "spiky" timeseries
spiky = [ \
    "proc.meminfo.memfree.None",
    "iostat.disk.read_requests.None",
    "proc.stat.cpu.type.system",
    "proc.stat.cpu.type.user",
    "proc.stat.cpu.type.iowait"]
#net.sockstat.num_sockets.type.tcp is just strange.

NormalTransform = LinearNormalize
BurstyTransform = LogTransform

transforms = dict()
transforms["None"] =                            Transform()
transforms["iostat.disk.read_requests"] =       BurstyTransform(0,1e2)
transforms["iostat.disk.write_requests"] =      BurstyTransform(0,1e2)
transforms["iostat.disk.msec_write"] =          BurstyTransform(0,1e4)
transforms["iostat.disk.msec_read"] =           BurstyTransform(0,1e5)
transforms["iostat.disk.read_sectors"] =        BurstyTransform(0,5e4)
transforms["iostat.disk.write_sectors"] =       BurstyTransform(0,5e4)
transforms["proc.loadavg.runnable"] =           NormalTransform(-4,4)
transforms["proc.meminfo.memfree"] =            NormalTransform(-1e5,1e5)
transforms["proc.meminfo.memtotal"] =           NormalTransform(0,1e8)
transforms["proc.meminfo.dirty"] =              NormalTransform(0,1e9)
transforms["proc.meminfo.cached"] =             NormalTransform(-1e5,1e5)
transforms["proc.meminfo.buffers"] =            NormalTransform(-1e2,1e2)
transforms["proc.stat.ctxt"] =                  NormalTransform(0,1e5)
transforms["proc.stat.intr"] =                  NormalTransform(-1e6,1e6)
transforms["proc.stat.procs_blocked"] =         NormalTransform(-0.1,0.1)
transforms["proc.stat.cpu.type.nice"] =         NormalTransform(0,10)
transforms["proc.stat.cpu.type.system"] =       BurstyTransform(0,20)
transforms["proc.stat.cpu.type.iowait"] =       BurstyTransform(0,20)
transforms["proc.stat.cpu.type.user"] =         BurstyTransform(0,20)
transforms["proc.stat.cpu,type.nice"] =         NormalTransform(0,10)
transforms["proc.stat.cpu,type.system"] =       BurstyTransform(0,20)
transforms["proc.stat.cpu,type.iowait"] =       BurstyTransform(0,20)
transforms["proc.stat.cpu,type.user"] =         BurstyTransform(0,20)
transforms["proc.net.packets.direction.out"] =  NormalTransform(0,1e4)
transforms["proc.net.packets.direction.in"] =   NormalTransform(0,1e4)
transforms["proc.net.packets,direction.out"] =  NormalTransform(0,1e4)
transforms["proc.net.packets,direction.in"] =   NormalTransform(0,1e4)
transforms["proc.loadavg.total_threads"] =      NormalTransform(-1e1,1e1)
transforms["proc.net.bytes.direction.in"] =     BurstyTransform(0,2e7)
transforms["proc.net.bytes.direction.out"] =    BurstyTransform(0,2e7)
transforms["proc.net.bytes,direction.in"] =     BurstyTransform(0,2e7)
transforms["proc.net.bytes,direction.out"] =    BurstyTransform(0,2e7)
transforms["net.sockstat.memory.type.tcp"] =    NormalTransform(0,1e6)
transforms["net.sockstat.num_sockets.type.tcp"]=NormalTransform(-0.2,0.1)

transforms["bytes_in"]=NormalTransform(0,5e7)
transforms["bytes_out"]=NormalTransform(0,5e7)
transforms["pkts_in"]=NormalTransform(0,1e4)
transforms["pkts_out"]=NormalTransform(0,1e4)
transforms["cpu_aidle"]=NormalTransform(0,100)
transforms["cpu_idle"]=NormalTransform(0,100)
transforms["cpu_nice"]=NormalTransform(0,100)
transforms["cpu_num"]=NormalTransform(0,100)
transforms["cpu_speed"]=NormalTransform(0,100)
transforms["cpu_system"]=NormalTransform(0,100)
transforms["cpu_user"]=NormalTransform(0,100)
transforms["cpu_wio"]=NormalTransform(0,100)
transforms["disk_req_read"]=NormalTransform(0,500)
transforms["disk_req_write"]=NormalTransform(0,500)
transforms["mem_buffers"]=NormalTransform(0,2e10)
transforms["mem_cached"]=NormalTransform(0,2e10)
transforms["mem_free"]=NormalTransform(0,2e10)
transforms["mem_shared"]=NormalTransform(0,2e10)
transforms["mem_total"]=NormalTransform(0,2e10)
transforms["dfs.datanode.reads_from_local_client"]=NormalTransform(0,10)
transforms["dfs.datanode.reads_from_remote_client"]=NormalTransform(0,10)
transforms["dfs.datanode.writes_from_local_client"]=NormalTransform(0,10)
transforms["dfs.datanode.writes_from_remote_client"]=NormalTransform(0,10)
transforms["dfs.datanode.bytes_read"]=NormalTransform(0,1e9)
transforms["dfs.datanode.bytes_written"]=NormalTransform(0,1e9)
transforms["disk_bytes_read"]=NormalTransform(0,1e9)
transforms["disk_bytes_write"]=NormalTransform(0,1e9)
transforms["proc_run"]=NormalTransform(0,100)
transforms["proc_total"]=NormalTransform(0,1000)

transforms["median"] = NormalTransform(0,0.1)

class DataMatrix:
    def __init__(self,datadir):
        self.datadir = datadir
        self.metrics = dict()
    
    def load(self):
        self.metrics = read_all_metric(self.datadir,"cloud1.") 

    #interptick: number of seconds per linear interpolation tick
    def flatten(self, interptick):
        (mnames, data, tsample) = flattenmetrics(self.metrics, interptick)
        self.mnames = mnames
        self.data = np.transpose(data)

    def print_metrics(self):
        print "Metrics: "
        for i in xrange(len(self.mnames)):
            print "  ", i, self.mnames[i]

    def print_stats(self):
        for i in xrange(len(self.mnames)):
            vs = self.data[:,i]
            minvs = min(vs)
            maxvs = max(vs)
            absg1 = ""
            if minvs < 0 or maxvs > 1:
                absg1 = "||>1"
            print "%2d %35s min=%.4f max=%.4f %4s" % \
                (i, self.mnames[i], minvs, maxvs, absg1)

    def get_data(self):
        return self.data

    #internally apply transforms to all metrics
    def transform_all(self):
        for i in xrange(len(self.mnames)):
            self.data[:,i]= self.transform(self.data[:,i], i)

    #transform data with the given attribute index
    # vs: data row to transform
    # attrdx: attribute index
    def transform(self, vs, attrdx):
        return self.get_transform(attrdx).apply(vs)

    def removeattrs(self, attrdxs):
        print len(self.mnames), self.data.shape
        self.mnames = np.delete(self.mnames, attrdxs)
        self.data = np.delete(self.data, attrdxs, 1)
        print len(self.mnames), self.data.shape

    def get_transform(self, attrdx):
        name = self.mnames[attrdx]
        trimsfx = ".None"
        if name.endswith(trimsfx):
            name = name[:-len(trimsfx)]
        if name in transforms:
            return transforms[name]
        else:
            print "No transform found for metric " + name
            return transforms["None"]

    #apply inverse of transform to vs
    def untransform(self, vs, attrdx):
        return self.get_transform(attrdx).unapply(vs)

    def attrname(self, i):
        return self.mnames[i]

    #get the number of attributes
    def nattrs(self):
        return len(self.mnames)

#get a list of all available metrics
def getmetrics():
    metrics = []
    itms = transforms.items()
    for (k,t) in itms:
        if k not in ["None",
            "net.sockstat.num_sockets.type.tcp",
            "net.sockstat.memory.type.tcp",
            "proc.meminfo.dirty",
            "proc.net.bytes.direction.in",
            "proc.net.bytes.direction.out",
            "proc.net.packets.direction.in",
            "proc.net.packets.direction.out",
            "proc.stat.cpu.type.iowait",
            "proc.stat.cpu.type.nice",
            "proc.stat.cpu.type.system",
            "proc.stat.cpu.type.user"]:
            metrics.append(k)
    return metrics

def printtransforms():
    metrics = getmetrics()
    metrics.sort()
    for i in xrange(len(metrics)):
        k = metrics[i]
        t = transforms[k]
        print k.replace("_","\\_"), "&", t.getname(), "&", int(t.lo), "&", int(t.hi), "\\\\"

if __name__ == "__main__":
    printtransforms()
