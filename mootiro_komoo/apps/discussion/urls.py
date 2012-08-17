# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('discussion.views',
    url(r'^discussion/(?P<identifier>\w+)/?$', 'discussion', name='discussion'),
)
