#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url

from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('komoo_project.views',
    url(r'^project/?$', 'project_list', name="project_list"),
    url(r'^project/new/?$', 'project_new', name="project_new"),

    url(r'^project/serach_tags/?$', 'tag_search', name='project_tag_search'),
    url(pr(r'^project/PROJECT_SLUG/?$'), 'project_view', name='project_view'),
    url(pr(r'^project/PROJECT_SLUG/edit/?$'), 'project_edit', name='project_edit'),
)
