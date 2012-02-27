#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *

from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('need.views',
    url(r'^need/new$', 'edit', name='new_need'),
    url(pr(r'^COMMUNITY_SLUG/need/NEED_SLUG/edit$'), 'edit', name='edit_need'),
    url(pr(r'^COMMUNITY_SLUG/need/NEED_SLUG$'), 'view', name='view_need'),
    url(pr(r'^COMMUNITY_SLUG/needs$'), 'list', name='list_needs'),
    url(r'^need/tag_search$', 'tag_search', name='need_tag_search'),
    url(r'^need/target_audience_search$', 'target_audience_search', name='target_audience_search'),
)
