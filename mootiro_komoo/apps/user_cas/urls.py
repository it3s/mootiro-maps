#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'django_cas.views.login'),
    url(r'^logout/$', 'django_cas.views.logout'),
)
urlpatterns += patterns('user_cas.views',
    # url(r'user/login$', 'login', name='login'),  #DEPRECATED
    # url(r'user/after_login$', 'after_login', name='after_login'),  #DEPRECATED
    # url(r'user/logout$', 'logout', name='logout'),  #DEPRECATED

    url(r'^test_login/$', 'test_login')
)
