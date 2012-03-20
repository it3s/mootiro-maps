#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import json
import logging

from django.contrib.gis.geos import Polygon, Point
from django.contrib.gis.measure import Distance
from django.db.models import Q
from django.http import HttpResponse
from django.forms.models import model_to_dict

from annoying.decorators import render_to

from community.forms import CommunityMapForm
from community.models import Community
from need.models import Need
from komoo_resource.models import Resource
from main.utils import create_geojson

logger = logging.getLogger(__name__)


@render_to('main/root.html')
def root(request):
    logger.debug('acessing Root')
    form = CommunityMapForm(request.POST)
    return dict(form=form)


def _fetch_geo_objects(Q):
    communities = Community.objects.filter(Q)
    needs = Need.objects.filter(Q)
    resources = Resource.objects.filter(Q)
    return dict(communities=communities, needs=needs, resources=resources)


def get_geojson(request):
    bounds = request.GET.get('bounds', None)
    x1, y2, x2, y1 = [float(i) for i in bounds.split(',')]
    polygon = Polygon(((x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)))

    intersects_polygon = (Q(points__intersects=polygon) |
                          Q(lines__intersects=polygon) |
                          Q(polys__intersects=polygon))

    d = _fetch_geo_objects(intersects_polygon)
    l = []
    for objs in d.values():
        l.extend(objs)
    geojson = create_geojson(l)
    return HttpResponse(json.dumps(geojson),
        mimetype="application/x-javascript")


def radial_search(request):
    center = Point(*[float(i) for i in request.GET['center'].split(',')])
    radius = Distance(m=float(request.GET['radius']))

    distance_query = (Q(points__distance_lte=(center, radius)) |
                      Q(lines__distance_lte=(center, radius)) |
                      Q(polys__distance_lte=(center, radius)))

    d = _fetch_geo_objects(distance_query)
    d = {
        'communities': [model_to_dict(c, fields=['name', 'slug']) for c in d['communities']],
        'needs': [model_to_dict(n, fields=['title', 'slug']) for n in d['needs']],
        'resources': [model_to_dict(r, fields=['title', 'slug']) for r in d['resources']],
    }
    return HttpResponse(json.dumps(d), mimetype="application/x-javascript")
