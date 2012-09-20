#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('user_cas.views',
    url(r'^login/?$', 'login', name="user_login"),
    url(r'^logout/?$', 'logout', name="user_logout"),

    url(r'^profile/update/?$', 'profile_update', name='profile_update'),
    url(r'^profile/update/public_settings/?$', 'profile_update_public_settings',
        name='profile_update_public_settings'),
    url(r'^profile/update/personal_settings/?$', 'profile_update_personal_settings',
        name='profile_update_personal_settings'),
    url(r'^profile/update/digest/?$', 'digest_update', name='digest_update'),
    url(r'^profile/signature/delete/?$', 'signature_delete',
        name='signature_delete'),
    url(r'profile/(?P<user_id>\d+)/?$', 'profile', name='user_profile'),
)
