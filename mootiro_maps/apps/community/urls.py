# -*- coding: utf-8 -*-
from django.conf.urls.defaults import url, patterns

from mootiro_maps.urls import prepare_regex as pr


urlpatterns = patterns('community.views',
    url(r'^new$', 'new_community', name='new_community'),
    url(r'^edit$', 'edit_community', name='edit_community'),
    url(r'^$', 'list', name='list_communities'),
    url(r'^search_by_name/?$', 'search_by_name',
            name='search_community_by_name'),
    url(r'^search_tags/?$', 'search_tags', name='community_search_tags'),
    url(r'^get_geojson/?$', 'communities_geojson', name='communities_geojson'),
    url(r'^get_name_for/(?P<id>\d+)/?$', 'get_name_for', name='get_name_for'),
    url(r'^autocomplete_get_or_add/?$', 'autocomplete_get_or_add',
        name='autocomplete_get_or_add'),

    url(pr(r'^ID/edit/?$'), 'edit_community', name='edit_community'),
    url(pr(r'^ID/about/?$'), 'view', name='view_community'),
    url(pr(r'^ID/?$'), 'on_map', name='community_on_map'),
)
