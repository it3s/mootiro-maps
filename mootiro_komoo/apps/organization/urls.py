# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('organization.views',
    url(r'^$', 'index'),
)
