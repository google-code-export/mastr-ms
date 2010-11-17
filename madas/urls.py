from django.conf.urls.defaults import * 
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

from madas.repository import admin as repoadmin

from madas.quote import admin as madasadmin

urlpatterns = patterns('',

#    (r'^(.*)/authorize', 'madas.madas.views.authorize'),
#    (r'^(.*)/index', 'madas.madas.views.serveIndex'),
    (r'^status/', status_view),
    (r'^sync/', include('madas.mdatasync_server.urls')),

    # madasrepo
    (r'^repo/', include('madas.repository.urls')),
    (r'^ws/', include('madas.repository.wsurls')),

    # admin
    (r'^repoadmin/', include(admin.site.urls)),

    #(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT, 'SSL' : True} ),
    # madas
)

# static
if settings.DEBUG:
    print 'Running with django view for static path.'
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT, 'SSL' : True} ),
    )

urlpatterns += patterns('', 
    (r'^', include('madas.quote.urls')),
    )
