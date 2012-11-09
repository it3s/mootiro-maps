#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import json
import logging

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Polygon
from django.db.models.query_utils import Q
from django.db.models import Count
from django.shortcuts import redirect

from django.contrib.contenttypes.models import ContentType
from projects.models import ProjectRelatedObject

from authentication.utils import login_required

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
    def on_get(request, form_community):
        form_community.helper.form_action = reverse('new_community')
        return form_community

    def on_after_save(request, obj):
        return {'redirect': reverse('view_community', args=(obj.id,))}

    return {'on_get': on_get, 'on_after_save': on_after_save}


@login_required
@ajax_form('community/edit.html', CommunityForm)
def edit_community(request, id='', *args, **kwargs):
    community = get_object_or_404(Community, pk=id) if id else Community()

    geojson = create_geojson([community], convert=False)
    if geojson and geojson.get('features'):
        geojson['features'][0]['properties']['userCanEdit'] = True
    geojson = json.dumps(geojson)

    def on_get(request, form_community):
        return CommunityForm(instance=community)

    def on_after_save(request, obj):
        url = reverse('view_community', args=(obj.id,))
        return {'redirect': url}

    return {'on_get': on_get, 'on_after_save': on_after_save,
            'community': community, 'geojson': geojson}


@render_to('community/on_map.html')
def on_map(request, id):
    community = get_object_or_404(Community, pk=id)
    geojson = create_geojson([community])
    return {
        'js_module': 'map/pages/map',  # Load map_page module using RequireJS
        'community': community,
        'geojson': geojson
    }


@render_to('community/view.html')
def view(request, id):
    community = get_object_or_404(Community, pk=id)
    geojson = create_geojson([community])
    photos = paginated_query(UploadedFile.get_files_for(community),
                             request, size=3)
    return {
        'js_module': 'community/pages/about',
        'community': community,
        'object': community,
        'geojson': geojson,
        'photos': photos
    }


@render_to('community/list.html')
def list(request):
    sort_order = ['creation_date', 'name']

    query_set = filtered_query(Community.objects, request)
    communities = sorted_query(query_set, sort_order, request)
    communities_count = communities.count()
    communities = paginated_query(communities, request)
    return dict(communities=communities, communities_count=communities_count)


@ajax_request
def projects(request, id):
    community = get_object_or_404(Community, pk=id)
    ct = ContentType.objects.get_for_model(community)
    return {'results': [p.project.as_dict for p in
        ProjectRelatedObject.objects.filter(content_type=ct,
                                            object_id=community.id)]}


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
    term = request.GET['term']
    communities = Community.objects.filter(Q(name__icontains=term) |
                                           Q(slug__icontains=term))
    d = [{'value': c.id, 'label': c.name} for c in communities]
    return HttpResponse(simplejson.dumps(d),
                        mimetype="application/x-javascript")


def search_tags(request):
    term = request.GET['term']
    qset = TaggedItem.tags_for(Community).filter(name__istartswith=term
            ).annotate(count=Count('taggit_taggeditem_items__id')
            ).order_by('-count', 'slug')[:10]
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
                mimetype="application/x-javascript")


# This is ever used????
@ajax_request
def autocomplete_get_or_add(request):
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
    community_name = Community.objects.get(pk=id).name
    return {'name': community_name}

