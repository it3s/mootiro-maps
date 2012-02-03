#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *
from django.views.generic import ListView
from .models import Proposal


urlpatterns = patterns('komoo.proposal.views',
    url(r'^proposal/new$', 'new', name='new_proposal'),
    url(r'^proposal/save$', 'save', name='save_proposal'),
    # url(r'^proposal/(?P<slug>\w+)/edit$', 'edit', name='edit_proposal'),
    (r'^proposals/$', ListView.as_view(model=Proposal,
        template_name='proposals_list.html')),
)
