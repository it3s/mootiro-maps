#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *


urlpatterns = patterns('komoo_map.views',
    url(r'^feature_types$', 'feature_types', name='feature_types'),
)
