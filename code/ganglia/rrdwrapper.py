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

import sys
import os
import time
import random
import rrdtool

class RRDWrapper():
    def create(self, filename, start, step=10):
        _start = int(start) / step * step
        ret = rrdtool.create(filename,
            "--step", str(step),
            "--start", str(start),
            "DS:sum:GAUGE:20:U:U",
            "RRA:AVERAGE:0.5:1:181440",
            "RRA:AVERAGE:0.5:12:181440");

    def update(self, filename, time, value, step=10):
        if (not os.path.exists(filename)):
            self.create(filename, time, step)
        time = time / step * step
        ret = rrdtool.update(filename, str(time)+":"+str(value))
        if ret:
            print rrdtool.error()

    def graph(self, filename, output, start, end, vlabel, name):
        ret = rrdtool.graph(output,
            "--start", str(start),
            "--end", str(end),
            "--vertical-label="+vlabel,
            "DEF:sum="+filename+":sum:AVERAGE",
            "AREA:sum#00FF00:"+name)

    def fetch(self, filename, start, end, step=10):
#        print filename, start, end, step
        ret = rrdtool.fetch(filename, "AVERAGE",
            "--start", str(start), "--end", str(end), "--r", str(step))
        return ret

def example():
    wrapper = RRDWrapper()
    now = int(time.time())
    filename = "test.rrd"
    # create a RRD file
    wrapper.create(filename, now)
    # insert 100 data points into the RRD file
    for i in range(1, 100):
        wrapper.update(filename, now+i*10, i)
    # draw a graph from the RRD file
    wrapper.graph(filename, "test.png", now, now+100*10, "#packets", "traffic")
    # fetch data from the RRD file
    print wrapper.fetch(filename, now+10, now+90*10)

if __name__=="__main__":
    example()
