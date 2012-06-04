#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('main.views',
    url(r'^$', 'root', name='root'),
    url(r'^stats$', 'stats', name='stats'),
    url(r'^get_geojson$', 'get_geojson', name='get_geojson'),
    url(r'^radial_search$', 'radial_search', name='radial_search'),
    url(r'^komoo_search/$', 'komoo_search', name='komoo_search'),
    url(r'^send_error_report/$', 'send_error_report', name='send_error_report'),
)

if settings.DEBUG:
    urlpatterns += patterns('main.views',
        url(r'^test/404$', 'test_404'),  # THIS is only for testing purposes
        url(r'^test/500$', 'test_500'),
    )
