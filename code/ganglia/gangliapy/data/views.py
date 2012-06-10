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

