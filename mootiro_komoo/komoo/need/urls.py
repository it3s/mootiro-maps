#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *
from ..urls import prepare_regex


urlpatterns = patterns('komoo.need.views',
    url(r'^need/new$', 'new', name='new_need'),
    url(r'^need/save$', 'save', name='save_need'),
    url(prepare_regex(r'^COMMUNITY_SLUG/need/NEED_SLUG$'),
        'view', name='view_need'),
    url(r'^need/tag_search$', 'tag_search', name='need_tag_search'),
)
