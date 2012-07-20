#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'django_cas.views.login'),
    # url(r'^logout/$', 'django_cas.views.logout'),
)
urlpatterns += patterns('user_cas.views',
    url(r'^logout/$', 'logout'),
    url(r'^profile/$', 'profile', name='user_profile'),
    url(r'^profile_update/$', 'profile_update', name='profile_update'),

)
