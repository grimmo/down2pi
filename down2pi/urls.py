from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from down2pi import views

urlpatterns = patterns('',
		    url(r'^$', views.index, name='index'),
                    #url(r'^ajax_durata_carrel/$', views.ajax_durata_carrel),
                    #url(r'^prenotazione/crea$', views.NuovaPrenotazione, name='nuova_prenotazione'),
                    url(r'^add$', views.add, name='add'),
                    url(r'^del/(?P<record_id>\d+)/$',views.dele,name='del'),
                    url(r'^edit/(?P<record_id>\d+)/$', views.edit,name='edit'),
                    url(r'^get_downloads/(?P<category>\w+)/$', views.get_downloads, name='get_downloads'),
                    url(r'^toggle_status/(?P<record_id>\d+)/(?P<status>\w+)/$', views.toggle_status, name='toggle_status'),
                    url(r'^expire/(?P<giorni>\d)/$', views.expire, name='expire'),
                    url(r'^logout/$', views.logout, name='logout'),
                    #url(r'^annulla_prenotazione/(?P<id_prenotazione>\d{1,})/(?P<token>[\w.:\-_=]+)/$',views.annulla_prenotazione,name='annulla_prenotazione'),
)
