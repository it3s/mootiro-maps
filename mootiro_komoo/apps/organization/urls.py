# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url
from mootiro_komoo.urls import prepare_regex as pr
from organization.views import Edit, New


urlpatterns = patterns('organization.views',
    url(r'^organization/?$', 'organization_list',
            name='organization_list'),
    url(r'^organization/new/?$', New.as_view(),
            name='organization_new'),
    url(r'^organization/edit/?$', Edit.as_view(),
            name='organization_edit'),
    url(r'^organization/(?P<organization_slug>[a-zA-Z0-9-]+)/?$', 'show',
            name='view_organization'),

    url(pr(r'^COMMUNITY_SLUG/organization/?$'), 'organization_list',
            name='organization_list'),
    url(pr(r'^COMMUNITY_SLUG/organization/new/?$'), New.as_view(),
            name='organization_new'),
    url(pr(r'^COMMUNITY_SLUG/organization/edit/?$'), Edit.as_view(),
            name='organization_edit'),
    url(pr(r'^COMMUNITY_SLUG/organization/(?P<organization_slug>[a-zA-Z0-9-]+)/?$'), 'show',
            name='view_organization'),
)
