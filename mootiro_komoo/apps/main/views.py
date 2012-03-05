#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import json
import logging

from django.contrib.gis.geos import Polygon
from django.db.models import Q
from django.http import HttpResponse

from annoying.decorators import render_to

from community.forms import CommunityMapForm
from community.models import Community
from need.models import Need

logger = logging.getLogger(__name__)


@render_to('main/root.html')
def root(request):
    logger.debug('acessing Root')
    form = CommunityMapForm(request.POST)

    return dict(form=form, current_item='map')


def get_geojson(request):
    bounds = request.GET.get('bounds', None)
    x1, y2, x2, y1 = [float(i) for i in bounds.split(',')]

    polygon = Polygon(((x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)))
    communities = Community.objects.filter(geometry__intersects=polygon)
    needs = Need.objects.filter(
            Q(points__intersects=polygon) |
            Q(lines__intersects=polygon)  |
            Q(polys__intersects=polygon)
    )
    geojson = {
        'type': 'FeatureCollection',
        'features': []
    }

    communities_features = [
        {
            'type': 'Feature',
            'geometry': json.loads(community.geometry.geojson),
            'properties': {
                'type': 'community',
                'name': community.name,
                'community_slug': community.slug
            }
        } for community in communities
    ]

    needs_features = [
        {
            'type': 'Feature',
            'geometry': json.loads(need.geometry.geojson)['geometries'][0],
            'properties': {
                'type': 'need',
                'name': need.title,
                'community_slug': need.community.slug,
                'need_slug': need.slug
            }
        } for need in needs
    ]

    geojson['features'] = communities_features + needs_features
    geojson = json.dumps(geojson)

    return HttpResponse(json.dumps(geojson),
        mimetype="application/x-javascript")
