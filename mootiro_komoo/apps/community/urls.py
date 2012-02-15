#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *

from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('community.views',
    url(r'^community/new$', 'edit', name='new_community'),
    url(pr(r'^COMMUNITY_SLUG/edit$'), 'edit', name='edit_community'),
    url(pr(r'^COMMUNITY_SLUG$'), 'view', name='view_community'),
    url(r'^community/map$', 'map', name='map_community'),
    url(r'^community/search_by_name$', 'search_by_name',
        name='search_community_by_name'),
)
