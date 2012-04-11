# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url

from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('investment.views',
    # editing
    # url(pr(r'^organization/ORGANIZATION_SLUG/investment/new/?$'),
    #         'edit', name='view_organization'),
    # url(pr(r'^COMMUNITY_SLUG/organization/ORGANIZATION_SLUG/investment/new?$'),
    #         'edit', name='view_organization'),
    url(pr(r'^need/NEED_SLUG/proposal/PROPOSAL_NUMBER/investment/new/?$'),
            'edit', name='new_proposal_investment'),
    url(pr(r'^COMMUNITY_SLUG/need/NEED_SLUG/proposal/PROPOSAL_NUMBER/investment/new/?$'),
            'edit', name='new_proposal_investment'),

    # viewing
    url(pr(r'^need/NEED_SLUG/proposal/PROPOSAL_NUMBER/investment/INVESTMENT_SLUG/?$'),
            'view', name='view_investment'),
    url(pr(r'^COMMUNITY_SLUG/need/NEED_SLUG/proposal/PROPOSAL_NUMBER/investment/INVESTMENT_SLUG/?$'),
            'view', name='view_investment'),
)
