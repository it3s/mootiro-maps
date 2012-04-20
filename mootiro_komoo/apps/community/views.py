#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import json
import logging

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Polygon
from django.db.models.query_utils import Q

from annoying.decorators import render_to, ajax_request
from fileupload.models import UploadedFile

from community.models import Community
from community.forms import CommunityForm
from main.utils import create_geojson, paginated_query

logger = logging.getLogger(__name__)


@login_required
def edit(request, community_slug=""):
    logger.debug('acessing Community > edit')

    if request.is_ajax():
        template = "community/edit_ajax.html"
    else:
        template = "community/edit.html"

    if community_slug:
        community = get_object_or_404(Community, slug=community_slug)
    else:
        community = Community(creator=request.user)

    if request.POST:
        form = CommunityForm(request.POST, instance=community)
        if form.is_valid():
            community = form.save()

            redirect_url = reverse('view_community', args=(community.slug,))
            if not request.is_ajax():
                return redirect(redirect_url)
            rdict = dict(redirect=redirect_url)
        else:
            rdict = dict(form=form, community=community)
    else:
        form = CommunityForm(instance=community)
        rdict = dict(form=form, community=community)
    geojson = create_geojson([community], convert=False)
    if geojson and geojson.get('features'):
        geojson['features'][0]['properties']['userCanEdit'] = True
    rdict['geojson'] = json.dumps(geojson)
    return render(request, template, rdict)


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
    communities = Community.objects.all().order_by('name')
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
