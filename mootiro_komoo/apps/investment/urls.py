# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url

from mootiro_komoo.urls import multiurls


from proposal.urls import home_urls as prop_prefs
from organization.urls import home_urls as org_prefs
# from resource.urls import home_urls as res_prefs
# org_prefs = []
res_prefs = []

pref_urls = prop_prefs + org_prefs + res_prefs
home_urls = [p + "investment/INVESTMENT_SLUG/" for p in pref_urls]


# prop_views = [
#     (r'investment/new/?$', 'edit', 'new_proposal_investment'),
#     (r'investment/INVESTMENT_SLUG/edit/?$', 'edit', 'edit_proposal_investment'),
#     (r'investment/INVESTMENT_SLUG/?$', 'view', 'view_proposal_investment'),
# ]
# org_views = [
#     (r'investment/new/?$', 'edit', 'new_organization_investment'),
#     (r'investment/INVESTMENT_SLUG/edit/?$', 'edit', 'edit_organization_investment'),
#     (r'investment/INVESTMENT_SLUG/?$', 'view', 'view_organization_investment'),
# ]
# res_views = [
#     (r'investment/new/?$', 'edit', 'new_resource_investment'),
#     (r'investment/INVESTMENT_SLUG/edit/?$', 'edit', 'edit_resource_investment'),
#     (r'investment/INVESTMENT_SLUG/?$', 'view', 'view_resource_investment'),
# ]
view_defs = [
    (r'investment/new/?$', 'edit', 'new_investment'),
    (r'investment/INVESTMENT_SLUG/edit/?$', 'edit', 'edit_investment'),
    (r'investment/INVESTMENT_SLUG/?$', 'view', 'view_investment'),
]

urlpatterns = patterns('investment.views',
    url(r'^investment/tag_search$', 'tag_search', name='investment_tag_search'),
    * (multiurls(pref_urls, view_defs))
    # * (multiurls(pref_urls, prop_views) +
    #    multiurls(pref_urls, org_views) + \
    #    multiurls(pref_urls, res_views))
)
