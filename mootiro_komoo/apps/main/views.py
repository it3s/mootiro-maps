#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import json
import logging

from django.contrib.gis.geos import Polygon, Point
from django.contrib.gis.measure import Distance
from django.db.models import Q
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from annoying.decorators import render_to, ajax_request
import requests

from community.models import Community
from need.models import Need
from komoo_resource.models import Resource
from organization.models import OrganizationBranch, Organization
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
    organization_branches = OrganizationBranch.objects.filter(Q) if zoom >= min_zoom else []
    return dict(communities=communities, needs=needs, resources=resources,
                organizations=organization_branches)


#@cache_page(54000)
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

    objs = _fetch_geo_objects(distance_query, 13)
    d = {}
    if 'communities' in request.GET:
        d['communities'] = objs['communities']
    if 'needs' in request.GET:
        need_categories = request.GET['need_categories'].split(',')
        d['needs'] = []
        for n in objs['needs']:
            if [c for c in n.categories.all() if str(c.id) in need_categories]:
                d['needs'].append(n)
    if 'organizations' in request.GET:
        d['organizations'] = objs['organizations']
    if 'resources' in request.GET:
        d['resources'] = objs['resources']

    return d


@render_to('404.html')
def test_404(request):
    return {}


@render_to('500.html')
def test_500(request):
    return {}


def _query_model(model, term, fields):
    query = Q()
    for field in fields:
        query_field = {'{}__icontains'.format(field): term}
        query |= Q(**query_field)
    return model.objects.filter(query).order_by(fields[0])


queries = {
    'organization': {
        'model': Organization,
        'query_fields': [
            'name',
            'slug',
            'description'
        ],
        'repr': 'name',
        'link': lambda o: reverse('view_organization',
                                  kwargs={'organization_slug': o.slug})
    },
    'resource': {
        'model': Resource,
        'query_fields': [
            'name',
            'description'
        ],
        'repr': 'name',
        'link': lambda o: reverse('view_resource',
                                  kwargs={'id': o.id})
    },
    'need': {
        'model': Need,
        'query_fields': [
            'title',
            'slug',
            'description'
        ],
        'repr': 'title',
        'link': lambda o: reverse('view_need',
                                  kwargs={'need_slug': o.slug})
    },
    'community': {
        'model': Community,
        'query_fields': [
            'name',
            'slug',
            'description'
        ],
        'repr': 'name',
        'link': lambda o: reverse('view_community',
                                  kwargs={'community_slug': o.slug})
    }
}


@ajax_request
def komoo_search(request):
    """
    search view for the index page.
    It uses the parameters from the 'queries' dict to perform specific
    queries on the database
    """
    logger.debug('Komoo_search: {}'.format(request.POST))
    term = request.POST.get('term', '')

    result = {}
    for key, model in queries.iteritems():
        result[key] = []
        for o in _query_model(model.get('model'), term, model.get('query_fields')):
            dados = {'id': o.id,
                     'name': getattr(o, model.get('repr')),
                     'link': model.get('link')(o),
                     'model': key}
            result[key].append(dados)

    # Google search
    google_results = requests.get(
        'https://maps.googleapis.com/maps/api/place/autocomplete/json',
        params={
            'input': term,
            'sensor': 'false',
            'types': 'geocode',
            'key': 'AIzaSyDgx2Gr0QeIASfirdAUoA0jjOs80fGtBYM',
        })
    result['google'] = google_results.content
    return {'result': result}
