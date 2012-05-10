#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import json
import logging

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Polygon
from django.db.models.query_utils import Q
from django.db.models import Count
from ajaxforms import ajax_form

from annoying.decorators import render_to, ajax_request
from fileupload.models import UploadedFile
from lib.taggit.models import TaggedItem

from community.models import Community
from community.forms import CommunityForm
from main.utils import (create_geojson, paginated_query, sorted_query,
                        filtered_query)

logger = logging.getLogger(__name__)


@login_required
@ajax_form('community/edit_ajax.html', CommunityForm)
def new_community(request, *args, **kwargs):
    logger.debug('acessing community > new_community')

    def on_get(request,  form_community):
        form_community.helper.form_action = reverse('new_community')
        return form_community

    def on_after_save(request, obj):
        return {'redirect': reverse('view_community', args=(obj.slug,))}

    return {'on_get': on_get, 'on_after_save': on_after_save}


@login_required
@ajax_form('community/edit.html', CommunityForm)
def edit_community(request, community_slug='', *args, **kwargs):
    logger.debug('acessing community > edit_community : community_slug={}'
        ''.format(community_slug))

    if community_slug:
        community = get_object_or_404(Community, slug=community_slug)
    else:
        community = Community()

    geojson = create_geojson([community], convert=False)
    if geojson and geojson.get('features'):
        geojson['features'][0]['properties']['userCanEdit'] = True
    geojson = json.dumps(geojson)

    def on_get(request, form_community):
        return CommunityForm(instance=community)

    def on_after_save(request, obj):
        url = reverse('view_community', args=(obj.slug,))
        return {'redirect': url}

    return {'on_get': on_get, 'on_after_save': on_after_save, 'community': community,
            'geojson': geojson}


@render_to('community/on_map.html')
def on_map(request, community_slug):
    logger.debug('acessing Community > on_map : community_slug={}'.format(
            community_slug))

    community = get_object_or_404(Community, slug=community_slug)
    geojson = create_geojson([community])
    return dict(community=community, geojson=geojson)


@render_to('community/view.html')
def view(request, community_slug):
    logger.debug('acessing Community > view : community_slug={}'.format(
            community_slug))

    community = get_object_or_404(Community, slug=community_slug)
    geojson = create_geojson([community])

    photos = paginated_query(UploadedFile.get_files_for(community),
                             request, size=3)
    return dict(community=community, geojson=geojson, photos=photos)


@render_to('community/map.html')
def map(request):
    logger.debug('acessing Community > map')
    return dict(geojson={})


@render_to('community/list.html')
def list(request):
    logger.debug('acessing community > list')

    sort_order = ['creation_date', 'name']

    query_set = filtered_query(Community.objects, request)
    communities = sorted_query(query_set, sort_order, request)
    communities_count = communities.count()
    communities = paginated_query(communities, request)
    return dict(communities=communities, communities_count=communities_count)


def communities_geojson(request):
    bounds = request.GET.get('bounds', None)
    x1, y2, x2, y1 = [float(i) for i in bounds.split(',')]
    polygon = Polygon(((x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)))
    # communities = Community.objects.filter(geometry__intersects=polygon)
    intersects_polygon = (Q(points__intersects=polygon) |
                          Q(lines__intersects=polygon) |
                          Q(polys__intersects=polygon))
    communities = Community.objects.filter(intersects_polygon)
    geojson = create_geojson(communities)
    return HttpResponse(json.dumps(geojson),
        mimetype="application/x-javascript")


def search_by_name(request):
    logger.debug('acessing Community > search_by_name')
    term = request.GET['term']
    # rx = "^{0}|\s{0}".format(term)  # matches only beginning of words
    # communities = Community.objects.filter(Q(name__iregex=rx) | Q(slug__iregex=rx))
    communities = Community.objects.filter(Q(name__icontains=term) |
                                           Q(slug__icontains=term))
    d = [{'value': c.id, 'label': c.name} for c in communities]
    return HttpResponse(simplejson.dumps(d), mimetype="application/x-javascript")


def search_by_tag(request):
    logger.debug('acessing resource > search_by_tag')
    term = request.GET['term']
    qset = TaggedItem.tags_for(Community).filter(name__istartswith=term
            ).annotate(count=Count('taggit_taggeditem_items__id')
            ).order_by('-count', 'slug')[:10]
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
                mimetype="application/x-javascript")


@ajax_request
def autocomplete_get_or_add(request):
    logger.debug('accessing community > add_new_from_autocomplete')
    logger.debug(request.POST)
    term = request.POST['name']
    communities = Community.objects.filter(Q(name__icontains=term) |
                                           Q(slug__icontains=term))
    if not communities.count():
        added = True
        #ADD new community
    else:
        added = False
    return dict(added=added)


@ajax_request
def get_name_for(request, id):
    logger.debug('acessing Community > get_name_for id: {}'.format(id))
    community_name = Community.objects.get(pk=id).name
    return {'name': community_name}
