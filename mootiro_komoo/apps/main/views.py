#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import json
import logging
from smtplib import SMTPException

from django.contrib.gis.geos import Polygon, Point
from django.contrib.gis.measure import Distance
from django.template import loader, Context
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.core.mail import mail_admins
from django.utils.translation import ugettext as _
from django.shortcuts import redirect
from django.contrib.auth.models import User

from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None
import requests

from community.models import Community
from need.models import Need
from proposal.models import Proposal
from organization.models import OrganizationBranch, Organization
from komoo_resource.models import Resource
from investment.models import Investment
from komoo_project.models import Project
from main.utils import create_geojson

logger = logging.getLogger(__name__)


ENTITY_MODEL = {
    'c': Community,
    'n': Need,
    'p': Proposal,
    'o': Organization,
    'b': OrganizationBranch,
    'r': Resource,
    'i': Investment,
    'j': Project,
    'u': User,
}
ENTITY_MODEL_REV = {v:k for k, v in ENTITY_MODEL.items()}


@render_to('main/root.html')
def root(request):
    logger.debug('acessing Root')
    return dict(community=None, geojson={})


def _fetch_geo_objects(Q, zoom):
    ret = {}
    for model in [Community, Need, Resource, OrganizationBranch]:
        ret[model.__name__] = model.objects.filter(Q)
    return ret


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

    objs = _fetch_geo_objects(distance_query, 100)
    d = {}
    if 'communities' in request.GET:
        d['Community'] = objs['Community']
    if 'needs' in request.GET:
        need_categories = request.GET['need_categories'].split(',')
        d['Need'] = []
        for n in objs['Need']:
            if [c for c in n.categories.all() if str(c.id) in need_categories]:
                d['Need'].append(n)
    if 'organizations' in request.GET:
        d['OrganizationBranch'] = objs['OrganizationBranch']
    if 'resources' in request.GET:
        d['Resource'] = objs['Resource']

    return d


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
                                  kwargs={'resource_id': o.id})
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
    },
    'user': {
        'model': User,
        'query_fields': [
            'username',
            'first_name',
            'last_name',
            'komooprofile__public_name'
        ],
        'repr': 'get_name',
        'link': lambda o: reverse('user_profile',
                                  kwargs={'username': o.username})
    }
}


def _has_geojson(obj):
    geometry = getattr(obj, 'geometry', '')
    return bool(geometry)


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
            dados = {
                'id': o.id,
                 'name': getattr(o, model.get('repr')),
                 'link': model.get('link')(o),
                 'model': key,
                 'has_geojson': _has_geojson(o),
                 'geojson': create_geojson([o])
            }
            if o.__class__.__name__ == 'Organization' and o.branch_count > 0:
                dados['branches'] = []
                for b in o.organizationbranch_set.all():
                    dados['branches'].append({
                        'id': b.id,
                        'name': getattr(b, model.get('repr')),
                        'model': key,
                        'has_geojson': _has_geojson(b),
                    })
            result[key].append(dados)

    # Google search
    google_results = requests.get(
        'https://maps.googleapis.com/maps/api/place/autocomplete/json',
        params={
            'input': term,
            'sensor': 'false',
            'types': 'geocode',
            'key': 'AIzaSyDgx2Gr0QeIASfirdAUoA0jjOs80fGtBYM',  # TODO: move to settings
        })
    result['google'] = google_results.content
    return {'result': result}


@ajax_request
def send_error_report(request):
    user = request.user
    user_message = request.POST.get('message', '')
    info = request.POST.get('info', '')
    url = request.POST.get('url', '')

    message = _("""
Url: {0}
Reporter: {1} (id: {2}, email: {3})
Info: {4}
Message: {5}
    """).format(url, user, user.id, user.email, info, user_message)

    try:
        mail_admins(_('Error report'), message, fail_silently=False)
        status = 'sent'
        success = 'true'
    except SMTPException:
        status = 'failed'
        success = 'false'
    finally:
        return {'status': status, 'success': success}


@render_to('404.html')
def test_404(request):
    return {}


@render_to('500.html')
def test_500(request):
    return {}


def custom_404(request):
    t = loader.get_template('404.html')
    c = Context({'request_path': request.path, 'STATIC_URL': '/static/'})
    return HttpResponseNotFound(t.render(c))


@render_to('500.html')
def custom_500(request):
    return {}


@render_to('not_anymore.html')
def permalink(request, identifier=''):
    url = 'root'
    if identifier:
        entity, id_ = identifier[0], identifier[1:]
        obj = get_object_or_None(ENTITY_MODEL[entity], pk=id_)
        if not obj:
            return {}
        url = getattr(obj, 'view_url', '/') if entity != 'u' \
                else reverse('user_profile', kwargs={'username': obj.username})
    return redirect(url)


@ajax_request
def get_geojson_from_hashlink(request):
    hashlink = request.GET.get('hashlink', '')
    if hashlink:
        obj = ENTITY_MODEL[hashlink[0]].objects.get(pk=hashlink[1:])
        geojson = create_geojson([obj])
    else:
        geojson = {}

    return {'geojson': geojson}

