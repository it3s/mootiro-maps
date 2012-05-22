#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import json
import logging

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Polygon

from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from lib.taggit.models import TaggedItem
from fileupload.models import UploadedFile
from ajaxforms import ajax_form

from community.models import Community
from need.models import Need, TargetAudience
from need.forms import NeedForm, NeedFormGeoRef
from main.utils import (create_geojson, paginated_query, sorted_query,
                        filtered_query, fix_community_url)

logger = logging.getLogger(__name__)


@login_required
@ajax_form('need/edit.html', NeedForm)
def new_need(request, community_slug="", need_slug=""):
    logger.debug('acessing need > new_need')

    community = get_object_or_None(Community, slug=community_slug)
    geojson = {}
    need = None

    def on_get(request, form):
        # if community:
            # logger.debug('community_slug: {}'.format(community_slug))
            # form.fields['community'].widget = forms.HiddenInput()
            # form.initial['community'] = community.id
        form.helper.form_action = reverse('new_need')
        return form

    def on_after_save(request, need):
        # args = (need.community.slug, need.slug) if need.community else (need.slug,)
        args = (need.slug, )
        redirect_url = reverse('view_need', args=args)
        return {'redirect': redirect_url}

    return {'on_get': on_get, 'on_after_save': on_after_save,
            'community': community, 'geojson': geojson, 'need': need}


@login_required
@ajax_form('need/edit_ajax.html', NeedFormGeoRef)
def new_need_from_map(request, community_slug="", need_slug=""):
    logger.debug('acessing need > new_need_from_map')

    community = get_object_or_None(Community, slug=community_slug)
    geojson, need = {}, None

    def on_get(request, form):
        # if community:
            # logger.debug('community_slug: {}'.format(community_slug))
            # form.fields['community'].widget = forms.HiddenInput()
            # form.initial['community'] = community.id
        form.helper.form_action = reverse('new_need_from_map')
        return form

    def on_after_save(request, need):
        # args = (need.community.slug, need.slug) if need.community else (need.slug,)
        args = (need.slug,)
        redirect_url = reverse('view_need', args=args)
        return {'redirect': redirect_url}

    return {'on_get': on_get, 'on_after_save': on_after_save,
            'community': community, 'geojson': geojson, 'need': need}


@login_required
@ajax_form('need/edit.html', NeedFormGeoRef)
def edit_need(request, community_slug="", need_slug=""):
    logger.debug('acessing need > new_need')

    community = get_object_or_None(Community, slug=community_slug)
    need = get_object_or_404(Need, slug=need_slug, community=community) \
                if community else get_object_or_404(Need, slug=need_slug)

    geojson = create_geojson([need], convert=False)
    if geojson and geojson.get('features'):
        geojson['features'][0]['properties']['userCanEdit'] = True
    geojson = json.dumps(geojson)

    def on_get(request, form):
        form = NeedFormGeoRef(instance=need)
        # if community:
            # logger.debug('community_slug: {}'.format(community_slug))
            # form.fields['community'].widget = forms.HiddenInput()
            # form.initial['community'] = community.id
        form.helper.form_action = reverse('new_need')
        return form

    def on_after_save(request, need):
        # args = (need.community.slug, need.slug) if need.community else (need.slug,)
        args = (need.slug,)
        redirect_url = reverse('view_need', args=args)
        return {'redirect': redirect_url}

    return {'on_get': on_get, 'on_after_save': on_after_save,
            'community': community, 'geojson': geojson, 'need': need}


@render_to('need/view.html')
def view(request, community_slug=None, need_slug=None):
    # if the need has no community pass an empty string
    logger.debug('acessing need > view')
    filters = dict(slug=need_slug)
    if community_slug:
        filters['community__slug'] = community_slug
    need = get_object_or_404(Need, **filters)
    geojson = create_geojson([need])
    photos = paginated_query(UploadedFile.get_files_for(need), request, size=3)
    community = get_object_or_None(Community, slug=community_slug)
    return dict(need=need, community=community, geojson=geojson, photos=photos)


@render_to('need/list.html')
@fix_community_url('list_community_needs')
def list(request, community_slug=''):
    logger.debug('acessing need > list')

    sort_fields = ['creation_date', 'title']

    if community_slug:
        community = get_object_or_404(Community, slug=community_slug)
        query_set = community.needs
    else:
        community = None
        query_set = Need.objects

    query_set = filtered_query(query_set, request)
    needs = sorted_query(query_set, sort_fields, request, default_order='title')
    needs_count = needs.count()
    needs = paginated_query(needs, request=request)
    return dict(community=community, needs=needs, needs_count=needs_count)


def tag_search(request):
    logger.debug('acessing need > tag_search')
    term = request.GET['term']
    qset = TaggedItem.tags_for(Need).filter(name__istartswith=term)
    # qset = TaggedItem.tags_for(Need)
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
                mimetype="application/x-javascript")


def target_audience_search(request):
    logger.debug('acessing need > target_audience_search')
    term = request.GET['term']
    qset = TargetAudience.objects.filter(name__istartswith=term)
    target_audiences = [ta.name for ta in qset]
    return HttpResponse(simplejson.dumps(target_audiences),
                mimetype="application/x-javascript")


def needs_geojson(request):
    bounds = request.GET.get('bounds', None)
    x1, y2, x2, y1 = [float(i) for i in bounds.split(',')]
    polygon = Polygon(((x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)))
    needs = Need.objects.filter(
            Q(points__intersects=polygon) |
            Q(lines__intersects=polygon) |
            Q(polys__intersects=polygon)
    )
    geojson = create_geojson(needs)
    return HttpResponse(json.dumps(geojson),
        mimetype="application/x-javascript")
