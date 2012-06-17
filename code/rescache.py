#!/usr/bin/python
'''
Result cache: serialization/datastore
'''

import numpy
import json
import os
import sys

class Cache:
    '''
    Store an analysis result in a folder to be viewed in UI
    '''
    def __init__(self, rootdir):
        '''
        Create a cache in the specified directory
        @param rootdir: the path to the cache (including its own dir name)
        '''
        self.rootdir = os.path.abspath(rootdir)
        self.SFX = ".json"
        self.statusloc = os.path.join(self.rootdir,"STATUS.json")

    def dump(self, name, obj):
        '''
        dump {obj} to the backing cache with key {name}
        '''
        with open(os.path.join(self.rootdir, name + self.SFX),"w") as fp:
            json.dump(obj, fp)

    def printstatus(self, txt, detail=None):
        '''
        write {txt} to the status output of the result
        @param txt: status text
        @param detail: additional detail
        '''
        todump = {}
        todump["status"] = txt
        if detail != None:
            todump["detail"] = detail

        with open(self.statusloc,"a") as fp:
            json.dump(todump, fp)
            fp.write("\n")

    def getstatus(self):
        '''
        Read the contents of the status file (for checking analysis status)
        '''
        results = []
        with open(self.statusloc,"r") as fp:
            for line in fp:
                results.append(json.loads(line))
        return results

    def load(self, name):
        '''
        Return an item from the backing cache with key {name}
        '''
        fname = os.path.join(self.rootdir, name + self.SFX)
        if not os.path.exists(fname):
            return None
        else:
            with open(fname,"r") as fp:
                res = json.load(fp)
                return res

    def write(self, output):
        '''
        cache pipeline output {output}
        '''
        tsnames = output["ts_names"]
        hvs = output["hvlog"]
        if hvs == None:
            hvs = []

        self.dump("index", {
            "mint": output["mint"],
            "maxt": output["maxt"],
            "step": output["maxt"],
            "ts_names": tsnames, 
            "hiddenvars": len(hvs)
        })
        self.dump("tsample", list(output["tsample"]))

        #ts_names should be in the same order
        #to ensure proper mapping
        #this is the last projection matrix
        self.dump("projection", output["projection"].tolist())

        data = output["data"]
        for i in xrange(len(tsnames)):
            name = tsnames[i]
            self.dump(name + ".smooth", list(data[i][0]))
            self.dump(name + ".spikes", list(data[i][1]))
            self.dump(name + ".residual", list(data[i][2]))
            self.dump(name + ".original", list(data[i][3]))
        
        for i in xrange(len(hvs)):
            self.dump("hv." + str(i), list(hvs[i]))

        if "predict" in output and output["predict"] != None:
            predict = output["predict"]
        else:
            predict = []
        for i in xrange(len(predict)):
            self.dump("predict." + str(i), list(predict[i]))

        if "heatmap" in output and output["heatmap"] != None:
            self.dump("heatmap", output["heatmap"].tolist())

    def getcontents(self):
        '''
        Get a list of readable file contents of this Cache
        '''
        fis = os.listdir(self.rootdir)
        sfxlen = len(self.SFX)
        names = []
        for f in fis:
            if f.endswith(self.SFX):
                names.append(f[:-sfxlen])
        return names

    def getsummary(self):
        '''
        Get a description of the contents of the cache to be loaded by the UI
        before loading any of the data.
        '''
        rdict = self.load("index")
        rdict["contents"] = self.getcontents()
        rdict["tsample"] = self.load("tsample")
        return rdict