# -*- coding: utf-8 -*-
from django.shortcuts import render,get_object_or_404
from down2pi.models import Download,URLForm,MultipleURLsForm,STATUS as valid_statuses
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseBadRequest
from django.template import RequestContext, loader
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.signing import Signer
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse_lazy
from django.core import serializers
from django.contrib.auth.views import logout_then_login
from django.utils import timezone
from django.forms.models import modelform_factory
#import datetime
from datetime import timedelta
import json

class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return self.render_to_json_response(data)
        else:
            return response

# Create your views here.

@login_required
def index(request):
    elenco = Download.objects.order_by('-data_creazione')
    template = loader.get_template('downloads/index.html')
    form = modelform_factory(Download,exclude=['status'])
    try:
        last_seen = Download.objects.all().order_by('-last_change').first().last_change
    except:
        last_seen = ''
    #if request.session.has_key('last_seen'):
    #    last_seen = datetime.datetime.strptime(request.session['last_seen'],'%Y%m%d %H:%M:%S')
    #else:
    #    last_seen = ''
    context = RequestContext(request, {'elenco': elenco,'form':form,'last_seen':last_seen})
    return HttpResponse(template.render(context))

@login_required
def add(request):
    if request.method == 'POST': # If the form has been submitted...
        AddURLForm = modelform_factory(Download,exclude=['status'])
        form = AddURLForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            form.save()
            elenco = Download.objects.order_by('data_creazione')
            if request.is_ajax():
                return render_to_response('downloads/lista.html', {'elenco': elenco}, context_instance=RequestContext(request))
            else:
                return render_to_response('downloads/index.html', {'elenco': elenco}, context_instance=RequestContext(request))
    else:
        return HttpResponse("This is a GET")

@login_required
def multiadd(request):
    if request.method == 'POST': # If the form has been submitted...
        form = MultipleURLsForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            AddURLForm = modelform_factory(Download,exclude=['status'])
            for splitted_url in form.data['url_list'].split('\r\n'):
                download_data = {'url':splitted_url,'status':'NEW','cat':form.data['cat'],'folder':form.data['folder']}
                download_form = AddURLForm(download_data)
                if download_form.is_valid():
                    d = download_form.save()
                else:
                    break
                    form.errors = download_form.errors
                    return render_to_response('downloads/multiple_form_add.html', {'form':form})
            elenco = Download.objects.order_by('data_creazione')
            if request.is_ajax():
                return render_to_response('downloads/lista.html', {'elenco': elenco}, context_instance=RequestContext(request))
            else:
                return render_to_response('downloads/index.html', {'elenco': elenco}, context_instance=RequestContext(request))
    else:
        form = MultipleURLsForm() 
        return render_to_response('downloads/multiple_add_form.html', {'form': form}, context_instance=RequestContext(request))
        #return HttpResponse("This is a GET")


@login_required
def edit(request,record_id):
    r = get_object_or_404(Download,pk=record_id)
    if request.method == 'POST': # If the form has been submitted...
        form = URLForm(request.POST,instance=r) # A form bound to the POST data and record instance, for updating
        if form.is_valid(): # All validation rules pass
            form.save()
            elenco = Download.objects.order_by('data_creazione')
            if request.is_ajax():
                return render_to_response('downloads/lista.html', {'elenco': elenco}, context_instance=RequestContext(request))
            else:
                return render_to_response('downloads/index.html', {'elenco': elenco}, context_instance=RequestContext(request))
        else:
            return render_to_response('downloads/edit_form.html', {'form': form}, context_instance=RequestContext(request))
    else:
        form = URLForm(instance=r) # A form bound to the specific record
        return render_to_response('downloads/edit_form.html', {'form': form,'record_id':r.id}, context_instance=RequestContext(request))

#class edit(AjaxableResponseMixin,UpdateView):
#    template_name = 'downloads/edit_form.html'
#    model = Download
#    fields = ['url','folder','cat']
    
@login_required
def view(request,pk):
    item = get_object_or_404(Download, pk=record_id)
    return render_to_response('downloads/lista.html',{'elenco':[item]}, context_instance=RequestContext(request))


@login_required
def dele(request,record_id):
    if request.method == 'POST': # If the form has been submitted...
        r = Download.objects.get(pk=record_id)
        esito = r.delete()
        elenco = Download.objects.order_by('data_creazione')
        if request.is_ajax():
            return render_to_response('downloads/lista.html', {'elenco': elenco}, context_instance=RequestContext(request))
        else:
            return render_to_response('downloads/index.html', {'elenco': elenco}, context_instance=RequestContext(request))
    else:
        return HttpResponse("You must use POST method to delete objects!")

#https://grimmo.pythonanywhere.com/default/call/json/get_downloads?download_type=Serie
def get_downloads(request,category):
    data = serializers.serialize('json',Download.ready.filter(cat=category).order_by('data_creazione'),fields=('url','cat','folder'))
    return HttpResponse(data, content_type='application/json')

def toggle_status(request,record_id,status):
    item = get_object_or_404(Download, pk=record_id)
    if status in [x[0] for x in valid_statuses]:
        item.status = status
        item.save()
        d = Download.objects.get(pk=record_id)
        data = serializers.serialize('json',Download.objects.filter(pk=record_id),fields=('status'))
    else:
        data = [{'success':False}]
    return HttpResponse(data, content_type='application/json')


def logout(request):
    return logout_then_login(request,'/accounts/login?next=/down2pi/', 'down2pi')

def expire(request,giorni):
    r = Download.objects.filter(data_creazione__lte=timezone.now()-timedelta(days=int(giorni))).exclude(status__in=('PRG','NEW'))
    esito = r.delete()
    elenco = Download.objects.order_by('data_creazione')
    if request.is_ajax():
        return render_to_response('downloads/lista.html', {'elenco': elenco}, context_instance=RequestContext(request))
    else:
        return HttpResponse(esito, content_type='application/json')
