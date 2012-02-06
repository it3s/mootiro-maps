#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *


urlpatterns = patterns('komoo.community.views',
    url(r'^community/new$', 'new', name='new_community'),
    url(r'^community/save$', 'save', name='save_community'),
    url(r'^(?P<slug>\w+)$', 'map'),
    url(r'^community/search_by_name$', 'search_by_name', name='search_community_by_name'),
)
