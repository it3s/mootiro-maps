#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import url, patterns
from django.conf import settings


urlpatterns = patterns('main.views',
    url(r'^map/$', 'map', name='map'),
    url(r'^get_geojson$', 'get_geojson', name='get_geojson'),
    url(r'^radial_search$', 'radial_search', name='radial_search'),
    url(r'^send_error_report/$', 'send_error_report',
                name='send_error_report'),
    url(r'^permalink/(?P<identifier>\w+)/?$', 'permalink', name='permalink'),
    url(r'^map/get_geojson_from_hashlink/?$', 'get_geojson_from_hashlink',
        name='get_geojson_from_hashlink'),
)


if settings.TESTING:
    # This is a little bit ugly but its for testing
    from .views import TestResourceHandler

    urlpatterns += patterns('',
        url(r'^test_resource/$', TestResourceHandler.dispatch),
    )

if settings.DEBUG:
    # THIS is only for testing purposes
    urlpatterns += patterns('main.views',
        url(r'^test/404$', 'test_404'),
        url(r'^test/500$', 'test_500'),
    )
