# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import url, patterns
from django.conf import settings


urlpatterns = patterns('search.views',
    url(r'^komoo_search/$', 'komoo_search', name='komoo_search'),
)

