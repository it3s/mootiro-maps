#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('authentication.views',
    # general urls
    url(r'^login/?$', 'login', name='user_login'),
    url(r'^logout/?$', 'logout', name='user_logout'),

    # user creation urls
    url(r'^new/?$', 'user_new', name='user_new'),
    url(r'^verification/?$', 'user_verification', name='user_check_inbox'),
    url(r'^verification/(?P<key>\S+)/?$', 'user_verification',
            name='user_verification'),

    # per user urls
    url(r'^(?P<id>\d+)/?$', 'profile', name='user_profile'),

    url(r'^edit/?$', 'profile_update', name='profile_update'),

    url(r'^edit/public_settings/?$',
            'profile_update_public_settings',
            name='profile_update_public_settings'),

    url(r'^edit/personal_settings/?$',
            'profile_update_personal_settings',
            name='profile_update_personal_settings'),

    url(r'^edit/digest_settings/?$', 'digest_update',
            name='digest_update'),

    url(r'^edit/signature_delete/?$', 'signature_delete',
        name='signature_delete'),

    # removable
    url(r'^explanations/?$', 'explanations', name='user explanations'),
)


urlpatterns += patterns('authentication.facebook',
    url(r'^login/facebook?$', 'login_facebook', name="login_facebook"),
    url(r'^login/facebook/authorized/?$', 'facebook_authorized',
                name="facebook_authorized"),
)

urlpatterns += patterns('authentication.google',
    url(r'^login/google?$', 'login_google', name="login_google"),
    url(r'^login/google/authorized/?$', 'google_authorized',
                name="google_authorized"),
)
