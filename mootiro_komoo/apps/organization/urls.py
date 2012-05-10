# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url
from mootiro_komoo.urls import prepare_regex as pr

home_urls = [
    r'^organization/ORGANIZATION_SLUG/',
    r'^COMMUNITY_SLUG/organization/ORGANIZATION_SLUG/'
]

urlpatterns = patterns('organization.views',
    url(r'^organization/?$', 'organization_list',
            name='organization_list'),
    url(r'^organization/new/?$', 'new_organization',
            name='new_organization'),

    # verify
    url(r'^organization/new/from_map/?$', 'new_organization_from_map',
            name='new_organization_from_map'),
    url(r'^organization/edit/?$', 'edit_organization',
            name='edit_organization'),

    url(r'^organization/edit_org/?$', 'edit_org',
            name='edit_org'),
    url(r'^organization/edit_branch/?$', 'edit_branch',
            name='edit_branch'),
    # end


    url(pr(r'^organization/ORGANIZATION_SLUG/?$'), 'show',
            name='view_organization'),
    url(r'^organization/branch/edit/$', 'edit_inline_branch',
            name='edit_inline_branch'),

    url(r'^organization/search_by_name/$', 'search_by_name',
            name='organization_search_by_name'),
    url(r'^organization/search_by_tag/$', 'search_by_tag',
            name='organization_search_by_tag'),

    url(pr(r'^COMMUNITY_SLUG/organization/?$'), 'organization_list',
            name='organization_list'),

    # verify
    url(pr(r'^COMMUNITY_SLUG/organization/new/?$'), 'new_organization',
            name='new_organization'),
    url(pr(r'^COMMUNITY_SLUG/organization/new/from_map/?$'), 'new_organization_from_map',
            name='new_organization_from_map'),
    url(pr(r'^COMMUNITY_SLUG/organization/edit/?$'), 'edit_organization',
            name='edit_organization'),
    # end

    url(pr(r'^COMMUNITY_SLUG/organization/ORGANIZATION_SLUG/?$'), 'show',
            name='view_organization'),
)
