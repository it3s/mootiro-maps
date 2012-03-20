#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('main.views',
    url(r'^$', 'root', name='root'),
    url(r'^get_geojson$', 'get_geojson', name='get_geojson'),
)

if settings.DEBUG:
    urlpatterns += patterns('main.views',
        url(r'^test/404$', 'test_404'),  # THIS is only for testing purposes
        url(r'^test/500$', 'test_500'),
    )
