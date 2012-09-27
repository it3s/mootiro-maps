#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import patterns, url
from mootiro_komoo.urls import prepare_regex as pr

# used for investments
home_urls = [pr(r'^resource/RESOURCE_ID/')]


urlpatterns = patterns('komoo_resource.views',
    url(r'resource/new/?$', 'new_resource', name='new_resource'),
    url(r'resource/new/from_map/?$', 'new_resource_from_map',
                name='new_resource_from_map'),
    url(pr(r'resource/RESOURCE_ID/edit/?$'), 'edit_resource',
                name='edit_resource'),
    url(pr(r'resource/RESOURCE_ID/?$'), 'show', name='view_resource'),
    url(r'resource/?$', 'resource_list', name='resource_list'),
    url(r'resources/?$', 'resources_to_resource',
                name='deprecated_resource_list'),
    url(r'^resource/search_by_kind/$', 'search_by_kind',
                name='resource_search_by_kind'),
    url(r'^resource/search_tags/$', 'search_tags',
                name='resource_search_tags'),
    # url(r'^resource/get_or_add_kind/$', 'resource_get_or_add_kind',
    #             name='resource_get_or_add_kind'),
)
