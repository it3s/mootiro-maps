#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *
from django.views.generic import ListView
from .models import Proposal
from ..urls import prepare_regex

prefix = prepare_regex(r'^need/NEED_SLUG/proposal/')

# TODO Finish adding prefix below
urlpatterns = patterns('komoo.proposal.views',
    url(prefix + r'new$', 'new', name='new_proposal'),
    url(prefix + r'save$', 'save', name='save_proposal'),
    url(r'^proposal/(?P<id>\d+)/edit$', 'edit', name='edit_proposal'),
    url(r'^proposal/(?P<id>\d+)/view$', 'view', name='view_proposal'),
    (r'^proposals/$', ListView.as_view(model=Proposal,
        template_name='proposals_list.html')),
)
