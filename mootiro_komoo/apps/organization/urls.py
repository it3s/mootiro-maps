# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url
from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('organization.views',
    url(r'^new/?$', 'new_organization', name='new_organization'),
    url(r'^new/from_map/?$', 'new_organization_from_map',
                name='new_organization_from_map'),
    url(r'^$', 'organization_list', name='organization_list'),
    url(r'^add_org_from_map/?$', 'add_org_from_map', name='add_org_from_map'),
    url(r'^add_branch_from_map/?$', 'add_branch_from_map',
                name='add_branch_from_map'),
    url(r'^branch/edit/$', 'edit_inline_branch', name='edit_inline_branch'),
    url(r'^verify_name/$', 'verify_org_name', name='verify_org_name'),
    url(r'^search_by_name/$', 'search_by_name',
            name='organization_search_by_name'),
    url(r'^search_tags/$', 'search_tags', name='organization_search_tags'),

    url(pr(r'^ID/edit/?$'), 'edit_organization', name='edit_organization'),
    url(pr(r'^ID/related/?$'), 'related_items',
                name='view_organization_related_items'),
    url(pr(r'^ID/?$'), 'show', name='view_organization'),
)

