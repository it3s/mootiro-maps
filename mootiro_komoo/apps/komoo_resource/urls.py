# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('komoo_resource.views',
    url(r'^new/?$', 'new_resource', name='new_resource'),
    url(r'^new/from_map/?$', 'new_resource_from_map',
                name='new_resource_from_map'),
    url(r'^$', 'resource_list', name='resource_list'),
    url(r'^search_by_kind/$', 'search_by_kind',
                name='resource_search_by_kind'),
    url(r'^search_tags/$', 'search_tags', name='resource_search_tags'),

    url(pr(r'^ID/edit/?$'), 'edit_resource', name='edit_resource'),
    url(pr(r'^ID/?$'), 'show', name='view_resource'),
)
