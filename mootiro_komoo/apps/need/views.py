#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import json
import logging

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.contrib.gis.geos import Polygon

from annoying.decorators import render_to
from taggit.models import TaggedItem

from community.models import Community
from need.models import Need, TargetAudience
from need.forms import NeedForm
from main.utils import create_geojson

logger = logging.getLogger(__name__)


@render_to('need/edit.html')
def edit(request, community_slug="", need_slug=""):
    logger.debug('acessing need > edit')
    community = get_object_or_404(Community, slug=community_slug) \
                    if community_slug else None
    need = get_object_or_404(Need, slug=need_slug, community=community) \
                if need_slug else None
    if request.POST:
        form = NeedForm(request.POST, instance=need)
        if form.is_valid():
            need = form.save()
            return {'redirect': reverse('view_need',
                    args=(need.community.slug, need.slug))}
        else:
            return {'form': form}
    else:
        form = NeedForm(instance=need)
        if community:
            form.fields.pop('community')
        return {'form': form}


@render_to('need/view.html')
def view(request, community_slug, need_slug):
    logger.debug('acessing need > view')
    community = get_object_or_404(Community, slug=community_slug)
    need = get_object_or_404(Need, slug=need_slug, community=community)
    return {'need': need}


@render_to('need/list.html')
def list(request, community_slug):
    logger.debug('acessing need > list')
    community = get_object_or_404(Community, slug=community_slug)
    needs = community.needs.all()
    return {'community': community, 'needs': needs}


# DOES NOT SIMPLY WORK WITH @ajax_request, please test before commit!
def tag_search(request):
    logger.debug('acessing need > tag_search')
    term = request.GET['term']
    qset = TaggedItem.tags_for(Need).filter(name__istartswith=term)
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
                mimetype="application/x-javascript")


# DOES NOT SIMPLY WORK WITH @ajax_request, please test before commit!
def target_audience_search(request):
    logger.debug('acessing need > target_audience_search')
    term = request.GET['term']
    qset = TargetAudience.objects.filter(name__istartswith=term)
    target_audiences = [ta.name for ta in qset]
    return HttpResponse(simplejson.dumps(target_audiences),
                mimetype="application/x-javascript")

def needs_geojson(request):
    bounds = request.GET.get('bounds', None)
    x1, y2, x2, y1 = [float(i) for i in bounds.split(',')]
    polygon = Polygon(((x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)))
    needs = Need.objects.filter(
            Q(points__intersects=polygon) |
            Q(lines__intersects=polygon)  |
            Q(polys__intersects=polygon)
    )
    geojson = create_geojson(needs)
    return HttpResponse(json.dumps(geojson),
        mimetype="application/x-javascript")


