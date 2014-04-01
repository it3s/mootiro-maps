# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('relations.views',
    url(r'^edit/?$', 'edit_relations', name='edit_relations'),
    url(r'^search/?$', 'search_relations', name='search_relations'),
)
