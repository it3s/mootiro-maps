# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url
from mootiro_komoo.urls import prepare_regex as pr

urlpatterns = patterns('organization.views',
    url(r'^organization/?$', 'index'),

    url(pr(r'^COMMUNITY_SLUG/organization/?$'), 'index'),
)
