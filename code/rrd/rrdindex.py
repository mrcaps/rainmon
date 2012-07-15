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

import os
from glob import glob

import rrdtool
import re

import unittest

"""
Collect metadata about RRD contents
"""

class RRDInfo:
    """
    Collect metadata from an RRD file
    """
    def __init__(self, fname=None):
        """
        if fname is not None, build from the given RRD file
        """
        self.dsets = dict()

        if fname != None:
            self.build_from_file(fname)
        else:
            fname = "unknown"
        self.fname = fname

    def build_from_file(self, fname):
        """
        Build RRD info from the given filename
        """
        info = rrdtool.info(fname)

        for (key, val) in info.iteritems():
            #ignore RRAs, and only examine ds[***] entries
            self.push_item(key, val)

    def push_item(self, key, val):
        #extract the dataset name
        keypath = key.split(".")
        first = keypath[0]
        match = re.match("ds\[(.+)\]", first)
        if match:
            ikey = match.group(1)
            if not ikey in self.dsets:
                self.dsets[ikey] = {}
            self.dsets[ikey][".".join(keypath[1:])] = val
            #print key, val

    def get_dset_names(self):
        return self.dsets.keys()

    def get_name(self):
        return self.fname

class RRDGroup:
    def __init__(self, dirname=None):
        self.infos = []

        if dirname != None:
            self.add_dir(dirname)
        else:
            dirname = "unknown"
        self.dirname = dirname

    def add_dir(self, fold):
        """
        Add a directory of RRDinfos

        (add all *.rrd files)
        """
        for fname in os.listdir(fold):
            fullpath = os.path.join(fold, fname)
            if os.path.splitext(fullpath)[-1] == ".rrd":
                self.infos.append(RRDInfo(fullpath))

    def add_info(self, info):
        """
        Add an RRDinfo to this group of RRDs
        """
        self.infos.append(info)

    def get_shared(self):
        """
        All dataset names that are shared by keys
        """
        keylst = [set(i.get_dset_names()) for i in self.infos]
        return set.intersection(*keylst)

    def get_unshared(self):
        """
        Non-shared keys, by dataset name
        """
        shared = self.get_shared()
        diffs = dict()

        for info in self.infos:
            name = info.get_name()
            if name in diffs:
                name += "+"
            diffs[name] = set.difference(set(info.get_dset_names()), shared)

        return diffs

    def includable(self, basedir=""):
        """
        Get an "include"-able representation of shared names and attributes 

        @param basedir: root dir of comp names
        """
        compnames = []
        for info in self.infos:
            n = os.path.splitext(info.fname)[0]
            if not n.startswith(basedir):
                print "WARNING: name %s does not start with basedir %s" % (n, basedir)
            else:
                n = n[len(basedir):]
            if n.startswith("/"):
                n = n[1:]

            compnames.append(n.replace("/","."))

        attrnames = list(self.get_shared())
        attrnames.sort()

        return (compnames, attrnames)

class TestRRDIndex(unittest.TestCase):
    def test_push(self):
        blank = RRDInfo()
        blank.push_item("ds[a].index",4)
        self.assertEqual(len(blank.dsets), 1)
        self.assertTrue(blank.dsets["a"])
        self.assertEqual(blank.dsets["a"]["index"], 4)

    def test_group(self):
        group = RRDGroup()
        i1 = RRDInfo()
        i1.push_item("ds[a].index",0)
        i1.push_item("ds[b].index",1)
        group.add_info(i1)

        i2 = RRDInfo()
        i2.push_item("ds[a].index",1)
        group.add_info(i2)

        i3 = RRDInfo()
        i3.push_item("ds[a].index",1)
        i3.push_item("ds[c].index",1)
        group.add_info(i3)

        shared = group.get_shared()
        self.assertEqual(len(shared), 1)
        self.assertTrue("a" in shared)

        unshared = group.get_unshared()
        self.assertEqual(len(unshared), 2)
        vals = unshared.values()
        self.assertEqual(len(vals[0]), 1)
        self.assertEqual(len(vals[1]), 1)

def run_individual(rrdpath):
    info = RRDInfo(rrdpath)
    for (ds, dct) in info.dsets.iteritems():
        print ds, dct

def run_folder(dirpath):
    group = RRDGroup()
    group.add_dir(os.path.join(dirpath, "dco"))

    (compnames, attrnames) = group.includable(basedir=dirpath)

    def format_list(lst):
        return ",\n".join(["\"%s\"" % i for i in lst])

    print "//Node names >>>\n"
    print format_list(compnames)

    print "//Attribute names >>>\n"
    print format_list(attrnames)

if __name__ == '__main__':
    #unittest.main()

    #run_individual("/home/bigubuntu/rrd/dco/dco-n100.rrd")
    run_folder("/home/bigubuntu/rrd")
