# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from mootiro_komoo.urls import prepare_regex as pr

home_urls = [
    r'^need/NEED_SLUG/proposal/PROPOSAL_NUMBER/',
]

urlpatterns = patterns('proposal.views',
    url(pr(r'^need/NEED_SLUG/proposal/new$'), 'edit',
            name='new_proposal'),

    url(pr(r'^need/NEED_SLUG/proposal/PROPOSAL_NUMBER/edit$'), 'edit',
            name='edit_proposal'),

    url(pr(r'^need/NEED_SLUG/proposal/PROPOSAL_NUMBER$'), 'view',
            name='view_proposal'),
)
