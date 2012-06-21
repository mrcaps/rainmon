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
# Created Time: 2012-01-14 15:13:30
# File Name: ./ganglia-rrd-manage.py
# Description:
#########################################################################
import time
from rrd import RRDWrapper

class RRDManager:
    def __init__(self, rootdir):
        self.rootdir = rootdir
        self.wrapper = RRDWrapper()

    def fetch(self, cluster, node, metric, start, end, step):
        filename="%s/%s/%s/%s.rrd"%(self.rootdir, cluster, node, metric)
        data = self.wrapper.fetch(filename, start, end, step)
        (rstart, rend, rstep) = data[0]
        tsdata = []
        for i in range(len(data[2])):
            if data[2][i][0] is None:
                tsdata.append("%s %d 0 host=%s\n"%(metric, rstart, node))
            else:
                tsdata.append("%s %d %lf host=%s\n"%(metric, rstart,
                                                data[2][i][0], node))
            rstart += rstep
        return tsdata

def test():
    manager = RRDManager('/mnt/data/ganglia/high')
    now = int(time.time())
    print manager.fetch('Compute Nodes', 'cloud43', 'bytes_in',
                        now-1000, now, 10)

if __name__=="__main__":
    test()
