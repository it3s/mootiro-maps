#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils import simplejson

from taggit.models import Tag

from komoo.community.models import Community
from komoo.need.models import Need
from komoo.need.forms import NeedForm


def new(request):
    context = {
        'form': NeedForm()
    }
    return render_to_response('need_edit.html', context,
            context_instance=RequestContext(request))

def save(request):
    form = NeedForm(request.POST)
    if form.is_valid():
        need = form.save()
        return redirect(view, need.community.slug, need.slug)
    else:
        return render_to_response('need_edit.html', dict(form=form),
            context_instance=RequestContext(request))

def view(request, community_slug, need_slug):
    community = Community.objects.get(slug=community_slug)
    need = Need.objects.get(community=community, slug=need_slug)
    return render_to_response('need_view.html', {'need': need})

def tag_search(request):
    # FIXME: get only tags related to needs
    term = request.GET['term']
    qset = Tag.objects.filter(name__istartswith=term)
    tags = [ t.name for t in qset ]
    return HttpResponse(simplejson.dumps(tags),
            mimetype="application/x-javascript")

