# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('proposal.views',
    url(pr(r'^new/?$'), 'edit', name='new_proposal'),
    url(pr(r'^ID/edit/?$'), 'edit', name='edit_proposal'),
    url(pr(r'^ID/?$'), 'view', name='view_proposal'),
)
