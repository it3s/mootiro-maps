# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('highlight.views',
    url(r'^object/?$', 'object_highlights', name='object_highlights'),
    url(r'^project/?$', 'project_highlights', name='project_highlights'),
)
