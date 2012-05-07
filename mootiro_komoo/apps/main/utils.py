#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import json
import re

from django.template.defaultfilters import slugify as simple_slugify
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponseRedirect

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset

try:
    from functools import wraps
except ImportError:
    def wraps(wrapped, assigned=('__module__', '__name__', '__doc__'),
              updated=('__dict__',)):
        def inner(wrapper):
            for attr in assigned:
                setattr(wrapper, attr, getattr(wrapped, attr))
            for attr in updated:
                getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
            return wrapper
        return inner


def slugify(term, slug_exists=lambda s: False):
    """Receives a term and a validator for the created slug in a namespace.
    Returns a slug that is unique according to the validator.
    """
    original = simple_slugify(term)
    slug = original
    n = 2
    # If needed, append unique number prefix to slug
    while slug_exists(slug):
        slug = re.sub(r'\d+$', '', slug)  # removes trailing '-number'
        slug = original + '-' + str(n)
        n += 1
    return slug


def create_geojson(objects, type_='FeatureCollection', convert=True):
    if type_ == 'FeatureCollection':
        geojson = {
            'type': 'FeatureCollection',
            'features': []
        }

        for obj in objects:
            if not hasattr(obj, 'geometry'):
                continue
            type_ = obj.__class__.__name__.lower()
            # geometry = json.loads(obj.geometry.geojson) if \
            #         type_ == 'community' else \
            #         json.loads(obj.geometry.geojson)['geometries'][0]
            geometry_json = json.loads(obj.geometry.geojson)
            #geometry = geometry_json['geometries'][0] if geometry_json['geometries'] else ''
            geometries = geometry_json['geometries']
            geometry = {}
            if geometries:
                if len(geometries) == 1:
                    geometry = geometries[0]
                else:
                    geometry_type = geometries[0]['type']
                    geometry['type'] = 'Multi{}'.format(geometry_type)
                    coord = []
                    for geom in geometries:
                        if geom['type'] == geometry_type:
                            coord.append(geom['coordinates'])
                    geometry['coordinates'] = coord
            else:
                continue
            name = getattr(obj, 'name', getattr(obj, 'title', ''))
            feature = {
                'type': 'Feature',
                'geometry': geometry,
                'properties': {
                    'type': type_,
                    'name': name,
                    'id': obj.id
                }
            }
            if hasattr(obj, 'community'):
                feature['properties']['community_slug'] = getattr(obj.community, 'slug', '')
            if hasattr(obj, 'slug'):
                feature['properties']['{}_slug'.format(type_)] = obj.slug
            if hasattr(obj, 'categories'):
                feature['properties']['categories'] = [{'name': c.name, 'image': c.image} for c in obj.categories.all()]
            if hasattr(obj, 'population'):
                feature['properties']['population'] = obj.population

            if type_ == 'organizationbranch':
                feature['properties']['organization_slug'] = obj.organization.slug
                feature['properties']['organization_name'] = obj.organization.name

            geojson['features'].append(feature)

    if convert:
        return json.dumps(geojson)

    return geojson


class MooHelper(FormHelper):
    def __init__(self, *a, **kw):
        retorno = super(MooHelper, self).__init__(*a, **kw)
        self.add_input(Submit('submit', 'Submit'))
        self.add_input(Reset('reset', 'Reset'))
        return retorno


def paginated_query(query, request=None, page=None, size=None):
    """
    Do the boring/repetitive pagination routine.
    Expects a request with page and size attributes
    params:
        query: any queryset objects
        request:  a django HttpRequest (GET)
           page: page attr on request.GET (default: 1)
           size: size attr on request.GET (default: 10)
        size: size of each page
        page: number of the current page
    """
    page = page or request.GET.get('page', '')
    size = size or request.GET.get('size', 10)

    paginator = Paginator(query, size)
    try:
        _paginated_query = paginator.page(page)
    except PageNotAnInteger:  # If page is not an integer, deliver first page.
        _paginated_query = paginator.page(1)
    except EmptyPage:  # If page is out of range, deliver last page
        _paginated_query = paginator.page(paginator.num_pages)
    return _paginated_query


date_order_map = {
    'desc': '-',
    'asc': ''
}


def sorted_query(query_set, sort_fields, request, default_order='name'):
    """
    Used for handle listing sorters
    params:
        query_set: any query set object or manager
        request: the HttpRequest obejct
    """
    sort_order = {k: i for i, k in enumerate(sort_fields)}
    sorters = request.GET.get('sorters', '')
    if sorters:
        sorters = sorted(sorters.split(','), key=lambda val: sort_order[val])

    for i, sorter in enumerate(sorters):
        if 'date' in sorter:
            date_order = request.GET.get(sorter, '-')
            sorters[i] = date_order_map[date_order] + sorter

    if sorters:
        return query_set.all().order_by(*sorters)
    else:
        return query_set.all().order_by(default_order)


def filtered_query(query_set, request):
    filters = request.GET.get('filters', '')
    for f in filters.split(','):
        if f == 'tags':
            request.encoding = 'latin-1'
            tags = request.GET.get('tags', '')
            if tags:
                tags = tags.split(',')
                query_set = query_set.filter(tags__name__in=tags)
        if f == 'community':
            community = request.GET.get('community', '')
            if community:
                query_set = query_set.filter(community=community)
    return query_set


def templatetag_args_parser(*args):
    """
    Keyword-arguments like function parser. Designed to be used in templatetags.
    Usage:

    def mytemplatetag(..., arg1='', arg2='', arg3=''):
        parsed_args = templatetag_args_parser(arg1, arg2, arg3)

        label = parsed_args.get('label', 'Default')
        use_border = parsed_args.get('use_border', False)
        zoom = parsed_args.get('zoom', 16)

    And in the template...
        {% mytemplatetag 'zoom=12' 'label=Your name' %}

    """
    parsed_args = {}
    for arg in args:
        if arg:
            a = arg.split('=')
            parsed_args[a[0]] = a[1]
    return parsed_args


def fix_community_url(view_name):
    def renderer(function):
        @wraps(function)
        def wrapper(request, community_slug='', *args, **kwargs):
            from community.models import Community

            comm_id = request.GET.get('community', '')
            comm = Community.objects.get(pk=comm_id) if comm_id else None
            if (community_slug and comm and comm.slug != community_slug) or (not community_slug and comm):
                current_url = request.get_full_path()
                url = reverse(view_name, kwargs={'community_slug': comm.slug})
                url += current_url[current_url.index('?'):]
                return HttpResponseRedirect(url)

            return function(request, community_slug=community_slug, *args, **kwargs)
        return wrapper
    return renderer
