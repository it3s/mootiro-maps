# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from mootiro_komoo.urls import prepare_regex as pr

home_urls = [
    r'^proposal/PROPOSAL_NUMBER/',
]

urlpatterns = patterns('proposal.views',
    url(pr(r'^proposal/new/?$'), 'edit', name='new_proposal'),

    url(pr(r'^proposal/ID/edit/?$'), 'edit', name='edit_proposal'),

    url(pr(r'^proposal/ID/?$'), 'view', name='view_proposal'),
)
