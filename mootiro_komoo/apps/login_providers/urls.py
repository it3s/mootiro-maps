# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('login_providers.facebook_views',
    url(r'^facebook?$', 'login_facebook', name="facebook_login"),
    url(r'^facebook/authorized?$', 'facebook_authorized', name="facebook_authorized"),
)

# urlpatterns += patterns('login_providers.google_views',
#     url(r'^google?$', 'login_google', name="google_login"),
#     url(r'^google/authorized?$', 'google_authorized', name="google_authorized"),
# )
