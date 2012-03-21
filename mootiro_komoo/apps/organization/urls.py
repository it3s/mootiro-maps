# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url
from mootiro_komoo.urls import prepare_regex as pr
from organization.views import Edit


urlpatterns = patterns('organization.views',
    url(r'^organization/?$', 'organization_list', name='organization_list'),
    url(r'^organization/edit/?$', Edit.as_view(), name='organization_edit'),

    url(pr(r'^COMMUNITY_SLUG/organization/?$'), 'organization_list',
                                                name='organization_list'),
    url(pr(r'^COMMUNITY_SLUG/organization/?$'), Edit.as_view(),
                                                name='organization_edit'),
)
