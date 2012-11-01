#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url

from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('projects.views',
    url(r'^$', 'project_list', name="project_list"),
    url(r'^new/?$', 'project_new', name="project_new"),
    url(r'^add_related/?$', 'add_related_object', name="project_add_related"),
    url(r'^delete_relations/?$', 'delete_relations', name='delete_relations'),
    url(r'^search_tags/?$', 'tag_search', name='project_tag_search'),
    url(r'^search_by_name/?$', 'search_by_name', name='search_by_name'),

    url(pr(r'^ID/?$'), 'project_view', name='project_view'),
    url(pr(r'^ID/edit/?$'), 'project_edit', name='project_edit'),
    url(pr(r'^ID/map/?$'), 'project_map', name='project_map'),
)
