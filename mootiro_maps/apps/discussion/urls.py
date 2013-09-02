# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('discussion.views',
    url(r'^(?P<identifier>\w+)/?$', 'view_discussion', name='view_discussion'),
    url(r'^(?P<identifier>\w+)/edit/?$', 'edit_discussion', name='edit_discussion'),
)
