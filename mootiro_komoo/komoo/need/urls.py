#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *


urlpatterns = patterns('komoo.need.views',
    url(r'^need/new$', 'new', name='new_need'),
    url(r'^need/save$', 'save', name='save_need'),
)
