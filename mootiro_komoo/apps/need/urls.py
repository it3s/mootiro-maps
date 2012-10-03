# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('need.views',
    url(r'^new/?$', 'new_need', name='new_need'),
    url(r'^new/from_map/?$', 'new_need_from_map',
            name='new_need_from_map'),

    url(r'^$', 'list', name='need_list'),

    url(r'^tag_search$', 'tag_search',
            name='need_tag_search'),
    url(r'^search_tags/?$', 'tag_search',
            name='need_tag_search'),
    url(r'^target_audience_search/?$', 'target_audience_search',
            name='target_audience_search'),
    url(r'^get_geojson$', 'needs_geojson', name='needs_geojson'),

    url(pr(r'^ID/edit/?$'), 'edit_need', name='edit_need'),

    url(pr(r'^ID/?$'), 'view', name='view_need'),
)
