#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils import simplejson

from taggit.models import Tag
from annoying.decorators import render_to, ajax_request

from community.models import Community
from need.models import Need
from need.forms import NeedForm


@render_to('need/need_edit.html')
def new(request):
    return{'form': NeedForm()}

@render_to('need/need_edit.html')
def save(request):
    form = NeedForm(request.POST)
    if form.is_valid():
        need = form.save()
        return redirect(view, need.community.slug, need.slug)
    else:
        return dict(form=form)

@render_to('need/need_view.html')
def view(request, community_slug, need_slug):
    community = Community.objects.get(slug=community_slug)
    need = Need.objects.get(community=community, slug=need_slug)
    return {'need': need}

@ajax_request
def tag_search(request):
    # FIXME: get only tags related to needs
    term = request.GET['term']
    qset = Tag.objects.filter(name__istartswith=term)
    tags = [ t.name for t in qset ]
    returntags
    # return HttpResponse(simplejson.dumps(tags),
    #         mimetype="application/x-javascript")

