from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect

#from django.contrib import admin
from down2pi import urls
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'panyw.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^down2pi/', include('down2pi.urls')),
#    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', lambda x: HttpResponseRedirect('/down2pi/')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
)
