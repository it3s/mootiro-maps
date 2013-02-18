# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import logging

from django.db.models import Q
from django.core.urlresolvers import reverse

from annoying.decorators import ajax_request
import requests

from authentication.models import User
from community.models import Community
from need.models import Need
from organization.models import Organization
from komoo_resource.models import Resource
from komoo_project.models import Project
from main.utils import create_geojson

logger = logging.getLogger(__name__)


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
        'link': lambda o: reverse('view_organization', kwargs={'id': o.id})
    },
    'resource': {
        'model': Resource,
        'query_fields': [
            'name',
            'description'
        ],
        'repr': 'name',
        'link': lambda o: reverse('view_resource', kwargs={'id': o.id})
    },
    'need': {
        'model': Need,
        'query_fields': [
            'title',
            'slug',
            'description'
        ],
        'repr': 'title',
        'link': lambda o: reverse('view_need', kwargs={'id': o.id})
    },
    'community': {
        'model': Community,
        'query_fields': [
            'name',
            'slug',
            'description'
        ],
        'repr': 'name',
        'link': lambda o: reverse('view_community', kwargs={'id': o.id})
    },
    'user': {
        'model': User,
        'query_fields': [
            'name',
        ],
        'repr': 'name',
        'link': lambda o: reverse('user_profile', kwargs={'id': o.id})
    },
    'project': {
        'model': Project,
        'query_fields': [
            'name',
            'slug',
            'description',
        ],
        'repr': 'name',
        'link': lambda o: reverse('project_view', kwargs={'id': o.id})
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
        for o in _query_model(model.get('model'),
                              term,
                              model.get('query_fields')):
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
            'key': 'AIzaSyDgx2Gr0QeIASfirdAUoA0jjOs80fGtBYM',
            # TODO: move to settings
        })
    result['google'] = google_results.content
    return {'result': result}
