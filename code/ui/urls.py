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
