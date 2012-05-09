#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *

from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('need.views',
    url(pr(r'^need/new/?$'), 'new_need',
            name='new_need'),
    url(pr(r'^need/new/from_map/?$'), 'new_need_from_map',
            name='new_need_from_map'),

    url(pr(r'^need/NEED_SLUG/edit/?$'), 'edit_need',
            name='edit_need'),
    url(pr(r'^COMMUNITY_SLUG/need/new/?$'), 'new_need',
            name='new_need'),
    url(pr(r'^COMMUNITY_SLUG/need/new/from_map/?$'), 'new_need_from_map',
            name='new_need_from_map'),
    url(pr(r'^COMMUNITY_SLUG/need/NEED_SLUG/edit/?$'), 'edit_need',
            name='edit_need'),

    url(pr(r'^need/NEED_SLUG/?$'), 'view',
            name='view_need'),
    url(pr(r'^COMMUNITY_SLUG/need/NEED_SLUG/?$'), 'view',
            name='view_need'),

    url(pr(r'^needs$'), 'list',
            name='list_all_needs'),
    url(pr(r'^COMMUNITY_SLUG/needs$'), 'list',
            name='list_community_needs'),

    url(r'^need/tag_search$', 'tag_search',
            name='need_tag_search'),
    url(r'^need/search_by_tag/$', 'tag_search',
            name='need_search_by_tag'),
    url(r'^need/target_audience_search$', 'target_audience_search',
            name='target_audience_search'),
    url(r'^need/get_geojson$', 'needs_geojson',
            name='needs_geojson'),
)
