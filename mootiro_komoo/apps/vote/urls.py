#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('vote.views',
    url(r'^$', 'vote_poc', name='vote_poc'),

)
