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

from community.models import Community
from need.models import Need
from komoo_resource.models import Resource
from organization.models import Organization
from main.utils import create_geojson

logger = logging.getLogger(__name__)


@render_to('main/root.html')
def root(request):
    logger.debug('acessing Root')
    return dict(geojson={})


def _fetch_geo_objects(Q, zoom):
    communities = Community.objects.filter(Q)
    # Fetch anything else communities only if zoom is greater than min zoom
    min_zoom = 13
    needs = Need.objects.filter(Q) if zoom >= min_zoom else []
    resources = Resource.objects.filter(Q) if zoom >= min_zoom else []
    organizations = Organization.objects.filter(Q) if zoom >= min_zoom else []
    return dict(communities=communities, needs=needs, resources=resources,
                organizations=organizations)


def get_geojson(request):
    bounds = request.GET.get('bounds', None)
    zoom = int(request.GET.get('zoom', 13))
    x1, y2, x2, y1 = [float(i) for i in bounds.split(',')]
    polygon = Polygon(((x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)))

    intersects_polygon = (Q(points__intersects=polygon) |
                          Q(lines__intersects=polygon) |
                          Q(polys__intersects=polygon))

    d = _fetch_geo_objects(intersects_polygon, zoom)
    l = []
    for objs in d.values():
        l.extend(objs)
    geojson = create_geojson(l)
    return HttpResponse(json.dumps(geojson),
        mimetype="application/x-javascript")


@render_to("main/filter_results.html")
def radial_search(request):
    center = Point(*[float(i) for i in request.GET['center'].split(',')])
    radius = Distance(m=float(request.GET['radius']))

    distance_query = (Q(points__distance_lte=(center, radius)) |
                      Q(lines__distance_lte=(center, radius)) |
                      Q(polys__distance_lte=(center, radius)))

    objs = _fetch_geo_objects(distance_query)
    d = {}
    if 'communities' in request.GET:
        d['communities'] = [model_to_dict(c, fields=['name', 'slug']) \
                                for c in objs['communities']]
    if 'needs' in request.GET:
        need_categories = request.GET['need_categories']
        d['needs'] = []
        for n in objs['needs']:
            if [c for c in n.categories.all() if str(c.id) in need_categories]:
                d['needs'].append(model_to_dict(n, fields=['title', 'slug']))
    if 'organizations' in request.GET:
        d['organizations'] = [model_to_dict(o, fields=['name', 'slug']) \
                                for o in objs['organizations']]
    if 'resources' in request.GET:
        d['resources'] = [model_to_dict(r, fields=['title', 'slug']) \
                            for r in objs['resources']]

    #return HttpResponse(json.dumps(d), mimetype="application/x-javascript")
    return objs


@render_to('404.html')
def test_404(request):
    return {}


@render_to('500.html')
def test_500(request):
    return {}
