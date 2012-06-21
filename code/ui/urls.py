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

from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^data$', 'ui.rain.views.data'),
    (r'^analyze$', 'ui.rain.views.analyze'),
    (r'^getsavenames$', 'ui.rain.views.getsavenames'),
    (r'^getstatus$', 'ui.rain.views.getstatus'),
    (r'^getsummary$', 'ui.rain.views.getsummary'),
    (r'^getprojection$', 'ui.rain.views.getprojection'),
    (r'^getheatmap$', 'ui.rain.views.getheatmap'),
    (r'^$', 'ui.rain.views.index'),
)
