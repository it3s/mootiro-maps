#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url

from mootiro_komoo.urls import prepare_regex as pr

from projects.api_views import *


urlpatterns = patterns('projects.api_views',
    url(pr(r'^(?P<pk>\d+)/?$'), ProjectItemView.as_view(), name='project_view')
)
