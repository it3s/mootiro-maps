#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('komoo_comments.views',
    url(r'^$', 'comments_index', name='comments_index'),
    url(r'^add/$', 'comments_add', name='comments_add'),
    url(r'^load/$', 'comments_load', name='comments_load'),

)
