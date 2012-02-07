#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson

from models import Community
from forms import CommunityForm


def new(request):
    context = {
        'form': CommunityForm()
    }
    return render_to_response('new.html', context,
            context_instance=RequestContext(request))

def save(request):
    community = CommunityForm(request.POST)
    community.save()
    return render_to_response('new.html')

def map(request, slug):
    community = Community.objects.get(slug=slug)
    return render_to_response('map.html', {'community': community},
            context_instance=RequestContext(request))

def search_by_name(request):
    term = request.GET['term']
    communities = Community.objects.filter(_name__istartswith=term)
    d = [ {'value': c.slug, 'label': c.name} for c in communities ]
    return HttpResponse(simplejson.dumps(d),
        mimetype="application/x-javascript")
