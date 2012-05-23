#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import patterns, url
from mootiro_komoo.urls import prepare_regex as pr

home_urls = [
    r'^resource/RESOURCE_ID/',
    r'^COMMUNITY_SLUG/resource/RESOURCE_ID/',
]

urlpatterns = patterns('komoo_resource.views',
    url(r'^resource/?$', 'resource_list', name='resource_list'),
    url(r'^resource/new/$', 'new_resource',
            name='new_resource'),
    url(r'^resource/edit/?$', 'edit_resource',
            name='edit_resource'),
    url(r'^resource/new/from_map/$', 'new_resource_from_map',
            name='new_resource_from_map'),

    url(pr(r'^resource/RESOURCE_ID/?$'), 'show', name='view_resource'),

    url(r'^resource/search_by_kind/$', 'search_by_kind',
            name='resource_search_by_kind'),
    url(r'^resource/search_tags/$', 'search_tags',
            name='resource_search_tags'),
    url(r'^resource/get_or_add_kind/$', 'resource_get_or_add_kind',
            name='resource_get_or_add_kind'),


    url(pr(r'^COMMUNITY_SLUG/resource/?$'), 'resource_list',
                name='resource_list'),
    url(pr(r'^COMMUNITY_SLUG/resource/new/$'), 'new_resource',
                name='new_resource'),
    url(pr(r'^COMMUNITY_SLUG/resource/edit/?$'), 'edit_resource',
                name='edit_resource'),
    url(pr(r'^COMMUNITY_SLUG/resource/new/from_map/$'), 'new_resource_from_map',
            name='new_resource_from_map'),

    url(pr(r'^COMMUNITY_SLUG/resource/RESOURCE_ID/?$'), 'show',
                name='view_resource'),
)
