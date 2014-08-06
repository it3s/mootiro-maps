# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('tracking.views',
    url(r'^redirect/?$', 'redirect', name='tracking_redirect'),
    url(r'^count_unique/?$', 'count_unique_visits', name='tracking_count_unique'),
    url(r'^count/?$', 'count_visits', name='tracking_count'),
    url(r'^list/?$', 'list_visits', name='tracking_list'),
)
