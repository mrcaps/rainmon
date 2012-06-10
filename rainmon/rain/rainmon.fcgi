#!/usr/bin/python
import sys
import os

sys.path.insert(0, '/home/rainmon/dj/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rain.settings'

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method = "threaded", daemonize = "false", maxchildren=3, minspare=0, maxspare=1)