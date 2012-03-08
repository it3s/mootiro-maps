#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import patterns, url
from komoo_resource.views import Edit
from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('komoo_resource.views',
    url(r'^resource/?$', 'resource_list', name='resource_list'),
    url(r'^resource/edit/?$', Edit.as_view(), name='resource_edit'),
    url(r'^resource/(?P<id>\d+)/?$', 'show', name='view_resource'),
    url(r'^resource/search_by_kind/$', 'search_by_kind', name='resource_search_by_kind'),
    url(r'^resource/search_by_tag/$', 'search_by_tag', name='resource_search_by_tag'),

    url(pr(r'^COMMUNITY_SLUG/resource/?$'), 'resource_list', name='list_community_needs'),
)
