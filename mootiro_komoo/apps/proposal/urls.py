#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.conf.urls.defaults import *
from django.views.generic import ListView
from proposal.models import Proposal
from mootiro_komoo.urls import prepare_regex

prefix = prepare_regex(r'^need/NEED_SLUG/proposal/')

urlpatterns = patterns('proposal.views',
    url(prefix + r'new$', 'new', name='new_proposal'),
    url(prefix + r'save$', 'save', name='save_proposal'),
    url(prefix + r'(?P<id>\d+)/edit$', 'edit', name='edit_proposal'),
    url(prefix + r'(?P<id>\d+)/view$', 'view', name='view_proposal'),
    (r'^proposals/$', ListView.as_view(model=Proposal, template_name='proposal/proposals_list.html')),
)
