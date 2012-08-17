#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url

from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('komoo_project.views',
    url(r'^project/?$', 'project_list', name="project_list"),
    url(r'^project/new/?$', 'project_new', name="project_new"),
    url(r'^project/add_related/?$', 'add_related_object',
        name="project_add_related"),
    url(r'^project/search_tags/?$', 'tag_search', name='project_tag_search'),
    url(r'^project/search_by_name/?$', 'search_by_name',
        name='search_by_name'),
    url(pr(r'^project/PROJECT_SLUG/?$'), 'project_view', name='project_view'),
    url(pr(r'^project/PROJECT_SLUG/edit/?$'), 'project_edit',
        name='project_edit'),
)
