#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('komoo_resource.views',
    url(r'^$', 'index', name='resource_index'),
    url(r'^edit/$', 'edit', name='resource_edit'),
)
