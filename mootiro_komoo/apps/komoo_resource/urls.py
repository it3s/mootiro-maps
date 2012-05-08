#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import patterns, url
from komoo_resource.views import Edit, New
from mootiro_komoo.urls import prepare_regex as pr

home_urls = [
    r'^resource/RESOURCE_ID/',
    r'^COMMUNITY_SLUG/resource/RESOURCE_ID/',
]

urlpatterns = patterns('komoo_resource.views',
    url(r'^resource/?$', 'resource_list', name='resource_list'),
    url(r'^resource/new/$', New.as_view(), name='resource_new'),

    url(r'^resource/new_resource/$', 'new_resource', name='new_resource'),

    url(r'^resource/edit/?$', Edit.as_view(), name='resource_edit'),
    url(pr(r'^resource/RESOURCE_ID/?$'), 'show', name='view_resource'),

    url(r'^resource/search_by_kind/$', 'search_by_kind',
            name='resource_search_by_kind'),
    url(r'^resource/search_by_tag/$', 'search_by_tag',
            name='resource_search_by_tag'),
    url(r'^resource/get_or_add_kind/$', 'resource_get_or_add_kind',
            name='resource_get_or_add_kind'),

    # this probably should be placed somewhere else (and made generic)
    url(r'^show_on_map/$', 'show_on_map', name='show_on_map'),

    url(pr(r'^COMMUNITY_SLUG/resource/?$'), 'resource_list',
                name='resource_list'),
    url(pr(r'^COMMUNITY_SLUG/resource/edit/?$'), Edit.as_view(),
                name='resource_edit'),
    url(pr(r'^COMMUNITY_SLUG/resource/new/$'), New.as_view(),
                name='resource_new'),
    url(pr(r'^COMMUNITY_SLUG/resource/RESOURCE_ID/?$'), 'show',
                name='view_resource'),
)
