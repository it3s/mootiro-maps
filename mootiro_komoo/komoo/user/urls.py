#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *

urlpatterns = patterns('komoo.user.views',
    url(r'user/login$', 'login', name='login'),
    url(r'user/after_login$', 'after_login', name='after_login'),
    url(r'user/logout$', 'logout', name='logout'),
)
