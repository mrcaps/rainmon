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
# Created Time: 2011-10-27 11:13:09
# File Name: ./read_data.py
# Description: 
#########################################################################

import os
import numpy

#read all datafiles from one metric directory
#name_prefix (optional) search by prefix of object name
def read_one_metric(metric_dir, name_prefix=""):
    metrics = []
    files = os.listdir(metric_dir)
    files.sort()
    for ff in files:
        if ff.endswith('npz') and ff.startswith(name_prefix):
            npzfile = numpy.load(metric_dir+'/'+ff)
            metrics.append((npzfile['x'], npzfile['y']))
    return metrics

#read all metrics
#name_prefix (optional) search by prefix of object name
def read_all_metric(data_dir, name_prefix=""):
    data_list = {}
    metric_list = os.listdir(data_dir)
    for metric in metric_list:
        subdir = os.path.join(data_dir, metric)
        if os.path.isdir(subdir):
            data_list[metric] = read_one_metric(subdir, name_prefix)
    return data_list
