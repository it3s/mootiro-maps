# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import patterns, url

from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('investment.views',
    url(r'^$', 'list', name='investment_list'),
    url(r'^tag_search$', 'tag_search', name='investment_tag_search'),
    url(r'^search_tags/?$', 'tag_search'),
    url(r'^new/?$', 'edit', name='new_investment'),
    url(pr(r'^ID/?$'), 'view', name='view_investment'),
    url(pr(r'^ID/edit/?$'), 'edit', name='edit_investment'),
)
