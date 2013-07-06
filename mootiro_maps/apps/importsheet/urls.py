# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import url, patterns
from mootiro_maps.urls import prepare_regex as pr


urlpatterns = patterns('importsheet.views',
    url(pr(r'^new/?$'), 'new', name='importsheet_new'),
    url(pr(r'^ID/?$'), 'show', name='importsheet_show'),
    url(pr(r'^ID/insert/?$'), 'insert', name='importsheet_insert'),
    url(pr(r'^ID/undo/?$'), 'undo', name='importsheet_undo'),
)

urlpatterns += patterns('importsheet.google',
    url(pr(r'^refresh_token/?$'), 'refresh_token',
            name='importsheet_refresh_token'),
    url(pr(r'^refresh_token_authorized/?$'), 'refresh_token_authorized',
            name='importsheet_refresh_token_authorized'),
)
