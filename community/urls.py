# Import django modules
from django.conf.urls.defaults import *

urlpatterns = patterns('mootiro_komoo.community.views',
    url(r'^community/new$', 'new', name='new_community'),
)
