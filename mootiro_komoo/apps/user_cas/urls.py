#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('',
    url(r'^login/$', 'django_cas.views.login'),
    # url(r'^logout/$', 'django_cas.views.logout'),
)
urlpatterns += patterns('user_cas.views',
    url(r'^logout/$', 'logout'),
    url(r'^profile/update/?$', 'profile_update', name='profile_update'),
    url(r'^profile/update/signatures/?$', 'profile_update_signatures',
        name='profile_update_signatures'),
    url(r'^profile/(?P<username>\w+)/?$', 'profile', name='user_profile'),
)
