#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('moderation.views',
    url(r'^moderation/report_content_box/$',
            'report_content_box', name='report_content_box'),
    url(r'^moderation/delete/(?P<app_label>.*)/(?P<model_name>.*)/(?P<obj_id>\d+)/$',
            'moderation_delete', name='moderation_delete'),
    url(r'^moderation/report/(?P<app_label>.*)/(?P<model_name>.*)/(?P<obj_id>\d+)/$',
            'moderation_report', name='moderation_report'),
)
