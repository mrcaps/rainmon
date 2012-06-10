#!/usr/bin/python
#########################################################################
# Author: Kai Ren
# Created Time: 2012-01-14 16:02:30
# File Name: ./query.py
# Description:
#########################################################################
import time
import string
from rrdmanager import RRDManager

class TSDBQuery:
    def __init__(self, rootdir, cluster):
        self.rootdir = rootdir
        self.cluster = cluster
        self.manager = RRDManager(rootdir)

    def fetch(self, request):
        (start, end, metrics) = self.parseURL(request)
        result = []
        for metric in metrics:
            metricname = metric[0]
            hosts = metric[1]['host'].split('|')
            for host in hosts:
                result.extend(self.manager.fetch(self.cluster, host, \
                              metricname, start, end, 10))
        return string.join(result, '')


    def parseURL(self, params):
        start = ''
        end = ''
        metrics = []
        param = str(params.GET['start'])
        start_tuple = time.strptime(param, "%Y/%m/%d-%H:%M:%S")
        start = int(time.mktime(start_tuple))
        param = str(params.GET['end'])
        end_tuple = time.strptime(param, "%Y/%m/%d-%H:%M:%S")
        end = int(time.mktime(end_tuple))
        param = str(params.GET['m'])
        param = param.replace("%7B","{").replace("%7D","}")
        tagpos = param.find('{')
        if tagpos < 0:
            pass
        else:
            tags = param[tagpos+1:-1]
            metricname=param[len('sum:'):tagpos]
            metrics.append((metricname, self.parseTags(tags)))
        return (start, end, metrics)

    def parseTags(self, tagstr):
        tags = tagstr.split(',')
        ret = {}
        for tag in tags:
            equalpos = tag.find('=')
            ret[tag[:equalpos]] = tag[equalpos+1:]
        return ret

class TestRequest:
    def __init__(self):
        self.GET = {}

def test():
    tsdbq = TSDBQuery('./testdir/', 'Compute Nodes')
    query = TestRequest()
    query.GET['start'] = '2012/01/14-17:00:00'
    query.GET['end'] = '2012/01/14-17:30:00'
    query.GET['m'] = 'sum:bytes_in{host=cloud41}'
    print tsdbq.fetch(query)

if __name__=="__main__":
    test()
