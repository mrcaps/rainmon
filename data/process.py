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

import string

def process_procstat_log(filename):
    num_ts = 0
    timeseries = [] 
    ts_mapping = {}
    f = open(filename, 'r')
    timestamp = 0
    lineno = 0
    for l in f:
        ll = l[:-1]
        lineno += 1
        if ll.isdigit():
            timestamp = int(l)
            continue
        items = ll.split()
        if len(items) == 1:
            pos = 0
            while (pos < len(ll)):
                if ll[pos] >= '0' and ll[pos] <= '9':
                    break
                pos += 1
            if pos < len(ll):
                if ll[pos:].isdigit():
                    timestamp = int(ll[pos:])
            continue 
        metric_name = string.join(items[0:-2])
        try:
            value = float(items[-1])
        except:
            print lineno
        if metric_name in ts_mapping:
            no = ts_mapping[metric_name]
        else:
            no = num_ts;
            num_ts += 1
            ts_mapping[metric_name] = no;
            timeseries.append(({}, [], []))
            timeseries[no][0]['metric'] = items[0] 
            for i in range(1, len(items) - 1):
                pos = items[i].find('=')
                tagname = items[i][0:pos]
                tagval = items[i][pos+1:]
                timeseries[no][0][tagname] = tagval 
        timeseries[no][1].append(timestamp)
        timeseries[no][2].append(value)
    f.close()
    return timeseries

ts = process_procstat_log("procstat-cloud9-2011-10-15.log")
for i in range(len(ts)):
    print ts[i][0]
