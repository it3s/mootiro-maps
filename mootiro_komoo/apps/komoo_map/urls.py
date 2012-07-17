#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *


urlpatterns = patterns('komoo_map.views',
    url(r'^feature_types/?$', 'feature_types', name='feature_types'),
    url(r'^tooltip/(?P<zoom>\d+)/(?P<app_label>.*)/(?P<model_name>.*)/(?P<obj_id>\d+)/?$', 'tooltip', name='tooltip'),
    url(r'^info_window/(?P<zoom>\d+)/(?P<app_label>.*)/(?P<model_name>.*)/(?P<obj_id>\d+)/?$', 'info_window', name='info_window'),
    url(r'^geojson/(?P<app_label>.*)/(?P<model_name>.*)/(?P<obj_id>\d+)/?$', 'geojson', name='geojson'),
)
