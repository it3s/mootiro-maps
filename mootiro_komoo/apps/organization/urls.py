# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url
from mootiro_komoo.urls import prepare_regex as pr


# used for investments
home_urls = [r'^organization/ORGANIZATION_SLUG/']


urlpatterns = patterns('organization.views',
    url(r'^organization/new/?$', 'new_organization', name='new_organization'),

    url(r'^organization/new/from_map/?$', 'new_organization_from_map',
                name='new_organization_from_map'),

    url(r'^organization/?$', 'organization_list', name='organization_list'),

    url(r'^organization/add_org_from_map/?$', 'add_org_from_map',
                name='add_org_from_map'),

    url(r'^organization/add_branch_from_map/?$', 'add_branch_from_map',
                name='add_branch_from_map'),

    url(r'^organization/branch/edit/$', 'edit_inline_branch',
                name='edit_inline_branch'),

    url(r'^organization/verify_name/$', 'verify_org_name',
                name='verify_org_name'),

    url(r'^organization/search_by_name/$', 'search_by_name',
                name='organization_search_by_name'),

    url(r'^organization/search_tags/$', 'search_tags',
                name='organization_search_tags'),

    url(pr(r'^organization/ID/edit/?$'), 'edit_organization',
                name='edit_organization'),

    url(pr(r'^organization/ID/related/?$'), 'related_items',
                name='view_organization_related_items'),

    url(pr(r'^organization/ID/?$'), 'show',
                name='view_organization'),
)

