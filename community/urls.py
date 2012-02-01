# Import django modules
from django.conf.urls.defaults import *

urlpatterns = patterns('mootiro_komoo.community.views',
    url(r'^community/new$', 'new', name='new_community'),
    url(r'^community/save$', 'save', name='save_community'),
    url(r'^community/(?P<slug>\w+)/edit$', 'edit', name='edit_community'),

    url(r'^(?P<slug>\w+)$', 'map')

)
