#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import patterns, url

from mootiro_komoo.urls import multiurls
from community.urls import home_urls as commu_prefs


pref_urls = commu_prefs + [r'^']
home_urls = [p + "resource/RESOURCE_ID/" for p in pref_urls]

view_defs = [
    (r'resource/new/?$', 'new_resource', 'new_resource'),
    (r'resource/new/from_map/?$', 'new_resource_from_map', 'new_resource_from_map'),
    (r'resource/RESOURCE_ID/edit/?$', 'edit_resource', 'edit_resource'),
    (r'resource/RESOURCE_ID/?$', 'show', 'view_resource'),
    (r'resource/?$', 'resource_list', 'resource_list'),
    (r'resources/?$', 'resources_to_resource', 'deprecated_resource_list'),
]

urlpatterns = patterns('komoo_resource.views',
    url(r'^resource/search_by_kind/$', 'search_by_kind', name='resource_search_by_kind'),
    url(r'^resource/search_tags/$', 'search_tags', name='resource_search_tags'),
    url(r'^resource/get_or_add_kind/$', 'resource_get_or_add_kind', name='resource_get_or_add_kind'),
    * (multiurls(pref_urls, view_defs))
)
