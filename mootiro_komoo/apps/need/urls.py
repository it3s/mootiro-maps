# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('need.views',
    url(r'^need/new/?$', 'new_need', name='new_need'),
    url(r'^need/new/from_map/?$', 'new_need_from_map',
            name='new_need_from_map'),
    url(pr(r'^need/NEED_SLUG/edit/?$'), 'edit_need',
            name='edit_need'),

    url(pr(r'^need/NEED_SLUG/?$'), 'view',
            name='view_need'),

    url(r'^need/?$', 'list', name='list_all_needs'),

    url(r'^need/tag_search$', 'tag_search',
            name='need_tag_search'),
    url(r'^need/search_tags/?$', 'tag_search',
            name='need_tag_search'),
    url(r'^need/target_audience_search/?$', 'target_audience_search',
            name='target_audience_search'),
    url(r'^need/get_geojson$', 'needs_geojson',
            name='needs_geojson'),
)
