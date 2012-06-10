#!/usr/bin/python
#########################################################################
# Author: Kai Ren
# Created Time: 2011-10-26 22:12:07
# File Name: ./crawl.py
# Description: 
#########################################################################

import string
import urllib
import numpy
import os

class QueryGenerator:
    def __init__(self, monitor_host, monitor_port):
        self.mhost = monitor_host
        self.mport = monitor_port
        self.metrics = []

    def clear(self):
        self.metrics = []

    def set_time(self, start, end):
        self.start = start
        self.end = end

    def add_metric(self, name, hosts, tags, isRate=False):
        if isRate:
            elm = "m=sum:rate:"
        else:
            elm = "m=sum:"
        if tags is None or tags == 'None':
            elm += "%s{%s}"%(name, hosts)
        else:
            elm += "%s{%s,%s}"%(name, tags, hosts)
        self.metrics.append(elm)

    def get_url(self):
        url = "http://%s:%s/q?start=%s&end=%s&%s&ascii"% \
            (self.mhost, self.mport, self.start, self.end, \
             string.join(self.metrics, '&'))
        return url

def load_metrics(filename):
    metric_list = []
    f = open(filename, "r")
    for l in f:
        items = l.split()
        print items
        metric_list.append(items)
    f.close()
    return metric_list

def download(url, filename):
    hosts = {}
    proxies = {'http': 'http://localhost:8888'}
    f = urllib.urlopen(url)
    for l in f:
        items = l.split()
        name = ""
        for i in range(3, min(5, len(items))):
            if items[i].startswith('host'):
                name = int(items[i][10:])
        if not name in hosts:
            hosts[name] = [[], []]
        hosts[name][0].append(int(items[1]))
        hosts[name][1].append(float(items[2]))
    f.close()
    outf = []
    hosts_list = hosts.keys()
    hosts_list.sort()
    outf.append(hosts_list)
    try:
        os.mkdir(filename)
    except Exception, e:
        print e
    for met in hosts_list:
        numpy.savez(filename+"/cloud"+str(met)+'.npz', 
                    x=hosts[met][0], y=hosts[met][1]) 

qgen = QueryGenerator('kmonitor', '4242')
qgen.set_time('2011/10/11-16:00:00', '2011/10/15-23:00:00')
metric_list = load_metrics('metrics1.txt')
host_list = []
for i in range(1, 65):
    host_list.append('cloud%d'%(i))
hosts = 'host='+string.join(host_list, '|')
for metric in metric_list:
    print metric
    qgen.clear()
    if metric[2] == 'True':
        isRate = True
    else:
        isRate = False
    qgen.add_metric(metric[0], hosts, metric[1], isRate)
    print qgen.get_url()
    download(qgen.get_url(), "%s.%s"%(metric[0], metric[1].replace('=','.')))
    print qgen.get_url()
