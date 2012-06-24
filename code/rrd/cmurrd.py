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
import math

IMPORTPATH = "../ganglia"
if IMPORTPATH not in sys.path:
        sys.path.append(IMPORTPATH)
from query import TSDBQuery

class FlatQuery(TSDBQuery):
	def __init__(self, rrdroot):
		self.rrdroot = rrdroot

	#get raw data from RRD
	def rrd_fetch(self, filename, start, end, step=10):
		try:
			ret = rrdtool.fetch(os.path.join(self.rrdroot,filename), "AVERAGE",
				"--start", str(start), "--end", str(end), "--r", str(step))
		except:
			print "Error", sys.exc_info()
			ret = ((0,0,0),[],[])
		return ret

	#filter metrics from an RRD file with multiple metrics
	def fetchmetrics(self, filename, start, end, metrics, step=10):
		raw = self.rrd_fetch(filename + ".rrd", start, end, step)
		(start,end,tick) = raw[0]
		mret = raw[1]
		dta = raw[2]
		#columns to pull from tuples
		cols = []
		for i in xrange(len(mret)):
			if mret[i] in metrics:
				cols.append(i)
		
		dlists = [[] * len(cols)]
		times = []
		timenow = start
		for datum in dta:
			for i in xrange(len(cols)):
				dlists[i].append(datum[cols[i]])
			times.append(timenow)
			timenow += tick

		return {
			"start": start,
			"end": end,
			"tick": tick,
			"dta": dlists,
			"times": times,
			"mnames": [mret[i] for i in cols]
		}

	#Format res (as obtained from fetchmetrics) in OpenTSDB response text
	# with the given host=hostname
	def format_tsdb(self, res, hostname, skipnan=True):
		lines = []
		metrics = res["mnames"]
		times = res["times"]
		for (metricdx, metric) in zip(xrange(len(metrics)), metrics):
			for i in xrange(len(times)):
				datum = res["dta"][metricdx][i]
				if datum == None:
					datum = float("NaN")
				if not (skipnan and math.isnan(datum)):
					lines.append("%s %d %f host=%s" % (metric, times[i], datum, hostname))
		return lines

	#Get results in OpenTSDB format - same interface as TSDBQuery
	def fetch(self, request):
		(start, end, metrics) = self.parseURL(request)
		result = []
		tstep = 10
		if "tstep" in request.GET:
			tstep = int(float(request.GET["tstep"]))

		#maintain host ordering - this could be more efficient.
		for metric in metrics:
			metricname = metric[0].replace("rate:","")
			print metricname
			hosts = metric[1]['host'].split('|')
			for host in hosts:
				result.extend(self.format_tsdb(self.fetchmetrics(host, \
					start, end, [metricname], tstep),host))
		return "\n".join(result)

def get_cmu():
	METRICS = ["uptime","loss","median"] #and ping1 through ping15...
	return FlatQuery("/home/bigubuntu/rrd")

def test_rrd_fetch():
	data = get_cmu()
	rawdata = data.rrd_fetch("LocalMachine",1327063033,1327081127)
	print "Time", rawdata[0]
	print "Metrics", rawdata[1]
	print "nmetrics", len(rawdata[1])
	nrows = 0
	rowlen = 0
	for row in rawdata[2]:
		rowlen = len(row)
		nrows += 1
	print "rowlen", rowlen
	print "nrows", nrows

def test_fetchmetrics():
	data = get_cmu()
	rawdata = data.fetchmetrics("LocalMachine",1327063033,1327081127,["median"])
	print rawdata

def test_fetchmetrics_tsdb():
	data = get_cmu()
	rawdata = data.fetchmetrics("LocalMachine",1327063033,1327073400,["median"])
	print data.format_tsdb(rawdata,"localmachine")

def test_request():
	data = get_cmu()
	class TestRequest:
		def __init__(self):
			self.GET = {}

	query = TestRequest()
	query.GET['start'] = '2012/01/20-8:30:00'
	query.GET['end'] = '2012/01/20-10:30:00'
	query.GET['m'] = 'sum:median{host=LocalMachine}'
	print data.fetch(query)

if __name__ == '__main__':
	#test_rrd_fetch()
	#test_fetchmetrics()
	#test_fetchmetrics_tsdb()
	test_request()