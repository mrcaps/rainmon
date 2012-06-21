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

from django.http import HttpResponse

IMPORTPATH = "../"
if IMPORTPATH not in sys.path:
        sys.path.append(IMPORTPATH)
from query import TSDBQuery

tsdbq = TSDBQuery('../testdir/', 'Compute Nodes')

def fetch(request):
    global tsdbq
#    print str(request)
#    return tsdbq.fetch('q?start=2012/01/14-17:00:00&end=2012/01/14-17:30:00&m=sum:bytes_in{host=cloud41}&ascii')
    return HttpResponse(tsdbq.fetch(request))

