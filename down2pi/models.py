from django.db import models
from django.forms import ModelForm
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator

# Create your models here.

STATUS = (('NEW','New'),('PRG','In progress'),('DONE','Completed'))
TYPES = (('serie','Serie TV'),('film','Film'),('other','Altro'))

class DownloadablesManager(models.Manager):
    def get_queryset(self):
        return super(DownloadablesManager, self).get_queryset().exclude(category='Other').filter(status='New').order_by('created_on')

class Download(models.Model):
    url = models.URLField(unique=True,max_length='255',help_text='URL da scaricare',validators=[URLValidator])
    status = models.CharField(choices=STATUS,max_length=4,editable=True,default='NEW')
    data_creazione = models.DateTimeField(auto_now_add=True,editable=False)
    last_change = models.DateTimeField(auto_now=True,blank=True,null=True,editable=False)
    cat = models.CharField(choices=TYPES,default='serie',max_length=5)
    folder = models.CharField(max_length=100,blank=True)

    def __unicode__(self):
        return u"%s %s (%s)" % (self.cat,self.url,self.status)

    def shorturl(self):
        if len(self.url) >=40:
            return u'%s(...)%s' % (self.url[0:4],self.url[self.url.rindex('/'):])
        else:
            return self.url

    def get_absolute_url(self):
        return self.url

    class Meta:
        verbose_name_plural = 'Downloads'

    objects = models.Manager() # The default manager.
    ready = DownloadablesManager() # Manager per link scaricabili

class URLForm(ModelForm):
    class Meta:
        model = Download
        fields = ['url','status','cat','folder']
