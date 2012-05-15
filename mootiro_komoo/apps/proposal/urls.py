#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *
from mootiro_komoo.urls import prepare_regex as pr

home_urls = [
    r'^need/NEED_SLUG/proposal/PROPOSAL_NUMBER/',
    r'^COMMUNITY_SLUG/need/NEED_SLUG/proposal/PROPOSAL_NUMBER/'
]

urlpatterns = patterns('proposal.views',
    url(pr(r'^need/NEED_SLUG/proposal/new$'), 'edit',
            name='new_proposal'),
    url(pr(r'^COMMUNITY_SLUG/need/NEED_SLUG/proposal/new$'), 'edit',
            name='new_proposal'),

    url(pr(r'^need/NEED_SLUG/proposal/PROPOSAL_NUMBER/edit$'), 'edit',
            name='edit_proposal'),
    url(pr(r'^COMMUNITY_SLUG/need/NEED_SLUG/proposal/PROPOSAL_NUMBER/edit$'), 'edit',
            name='edit_proposal'),

    url(pr(r'^need/NEED_SLUG/proposal/PROPOSAL_NUMBER$'), 'view',
            name='view_proposal'),
    url(pr(r'^COMMUNITY_SLUG/need/NEED_SLUG/proposal/PROPOSAL_NUMBER$'), 'view',
            name='view_proposal'),
)
