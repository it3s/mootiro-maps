# -*- coding: utf-8 -*-
from django.conf.urls.defaults import url, patterns

from mootiro_komoo.urls import prepare_regex as pr

# used by investments ?
home_urls = [r'^COMMUNITY_SLUG/']

urlpatterns = patterns('community.views',
    url(r'^community/new$', 'new_community', name='new_community'),
    url(r'^community/edit$', 'edit_community', name='edit_community'),

    url(r'^community/?$', 'list', name='list_communities'),

    url(r'^community/search_by_name/?$', 'search_by_name',
                name='search_community_by_name'),
    url(r'^community/search_tags/?$', 'search_tags',
                name='community_search_tags'),
    url(r'^community/get_geojson/?$', 'communities_geojson',
                name='communities_geojson'),
    url(r'^community/get_name_for/(?P<id>\d+)/?$', 'get_name_for',
                name='get_name_for'),
    url(r'^community/autocomplete_get_or_add/?$', 'autocomplete_get_or_add',
        name='autocomplete_get_or_add'),

    url(pr(r'^community/ID/edit/?$'), 'edit_community',
                name='edit_community'),
    url(pr(r'^community/ID/about/?$'), 'view', name='view_community'),
    url(pr(r'^community/ID/?$'), 'on_map', name='community_on_map'),
)
