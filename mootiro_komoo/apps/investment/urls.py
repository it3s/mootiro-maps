# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url

from mootiro_komoo.urls import prepare_regex as pr
from mootiro_komoo.urls import multiurls

from proposal.urls import home_urls as prop_prefs
from organization.urls import home_urls as org_prefs
from komoo_resource.urls import home_urls as res_prefs

pref_urls = prop_prefs + org_prefs + res_prefs
home_urls = [p + "investment/INVESTMENT_SLUG/" for p in pref_urls]

view_defs = [
    (r'investment/new/?$', 'edit', 'new_investment'),
    (r'investment/INVESTMENT_SLUG/edit/?$', 'edit', 'edit_investment'),
    (r'investment/INVESTMENT_SLUG/?$', 'view', 'view_investment'),
]

urlpatterns = patterns('investment.views',
    url(pr(r'^COMMUNITY_SLUG/investments/?$'), 'list', name='investment_list'),
    url(r'^investments/?$', 'list', name='investment_list'),
    url(r'^investment/tag_search$', 'tag_search', name='investment_tag_search'),
    url(r'^investment/search_tags/?$', 'tag_search'),
    * (multiurls(pref_urls, view_defs))
)
