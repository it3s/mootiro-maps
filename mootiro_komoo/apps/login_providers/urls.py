# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('login_providers.facebook',
    url(r'^facebook?$', 'login_facebook', name="login_facebook"),
    url(r'^facebook/authorized?$', 'facebook_authorized', name="facebook_authorized"),
)

# urlpatterns += patterns('login_providers.google_views',
#     url(r'^google?$', 'login_google', name="login_google"),
#     url(r'^google/authorized?$', 'google_authorized', name="google_authorized"),
# )
