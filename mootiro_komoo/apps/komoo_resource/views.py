# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import json

from django.views.generic import View
from django.db.models.query_utils import Q
from django.shortcuts import (render_to_response, RequestContext, HttpResponse,
        HttpResponseRedirect, get_object_or_404)
from django.utils import simplejson
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models import Count
from django.core.urlresolvers import reverse

from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None
from lib.taggit.models import TaggedItem
from ajaxforms import ajax_form

from komoo_resource.models import Resource, ResourceKind
from komoo_resource.forms import FormResource, FormResourceGeoRef
from main.utils import (create_geojson, paginated_query, sorted_query,
                        filtered_query, fix_community_url)
from community.models import Community
from fileupload.models import UploadedFile


logger = logging.getLogger(__name__)


def prepare_resource_objects(community_slug="", resource_id=""):
    """Retrieves a tuple (resource, community). According to given
    parameters may raise an 404. Creates a new resource if resource_id is
    evaluated as false."""
    community = get_object_or_None(Community, slug=community_slug)
    if resource_id:
        filters = dict(id=resource_id)
        if community:
            filters["community"] = community
        resource = get_object_or_404(Resource, **filters)
    else:
        resource = Resource(community=community)
    return resource, community


@render_to('resource/list.html')
@fix_community_url('resource_list')
def resource_list(request, community_slug=''):
    logger.debug('acessing komoo_resource > list')

    sort_order = ['creation_date', 'name']

    if community_slug:
        logger.debug('community_slug: {}'.format(community_slug))
        community = get_object_or_404(Community, slug=community_slug)
        query_set = Resource.objects.filter(community=community)
    else:
        community = None
        query_set = Resource.objects

    query_set = filtered_query(query_set, request)

    resources_list = sorted_query(query_set, sort_order, request)
    resources_count = resources_list.count()
    resources = paginated_query(resources_list, request)

    return dict(resources=resources, community=community,
                resources_count=resources_count)


@render_to('resource/show.html')
def show(request, community_slug=None, resource_id=None):
    logger.debug('acessing komoo_resource > show')

    resource = get_object_or_404(Resource, pk=resource_id)
    geojson = create_geojson([resource])
    similar = Resource.objects.filter(Q(kind=resource.kind) |
        Q(tags__in=resource.tags.all())).exclude(pk=resource.id).distinct()[:5]
    community = get_object_or_None(Community, slug=community_slug)
    photos = paginated_query(UploadedFile.get_files_for(resource), request, size=3)

    return dict(resource=resource, similar=similar, geojson=geojson,
                community=community, photos=photos)


@login_required
@ajax_form('resource/new.html', FormResource, 'form_resource')
def new_resource(request, community_slug='', *arg, **kwargs):
    logger.debug('acessing komoo_resource > new_resource')
    community = get_object_or_None(Community, slug=community_slug)

    def on_get(request, form_resource):
        if community:
            logger.debug('community_slug: {}'.format(community_slug))
            form_resource.fields['community'].widget = forms.HiddenInput()
            form_resource.initial['community'] = community.id
        form_resource.helper.form_action = reverse('new_resource')
        return form_resource

    def on_after_save(request, obj):
        prefix = '/{}'.format(community_slug) if community_slug else ''
        _url = '{}/resource/{}'.format(prefix, obj.id)
        return {'redirect': _url}

    return {'on_get': on_get, 'on_after_save': on_after_save,
            'community': community}


@login_required
@ajax_form('resource/new_frommap.html', FormResourceGeoRef, 'form_resource')
def new_resource_from_map(request, community_slug='', *args, **kwargs):
    logger.debug('acessing komoo_resource > new_resource_from_map')
    community = get_object_or_None(Community, slug=community_slug)

    def on_get(request, form_resource):
        if community:
            logger.debug('community_slug: {}'.format(community_slug))
            form_resource.fields['community'].widget = forms.HiddenInput()
            form_resource.initial['community'] = community.id
        form_resource.helper.form_action = reverse('new_resource_from_map')
        return form_resource

    def on_after_save(request, obj):
        prefix = '/{}'.format(community_slug) if community_slug else ''
        _url = '{}/resource/{}'.format(prefix, obj.id)
        return {'redirect': _url}

    return {'on_get': on_get, 'on_after_save': on_after_save,
            'community': community}


@login_required
@ajax_form('resource/edit.html', FormResourceGeoRef, 'form_resource')
def edit_resource(request, community_slug='', *arg, **kwargs):
    logger.debug('acessing komoo_resource > edit_resource')
    community = get_object_or_None(Community, slug=community_slug)
    geojson = {}

    _id = request.GET.get('id', 0)
    resource = get_object_or_None(Resource, pk=_id)

    geojson = create_geojson([resource], convert=False)
    if geojson and geojson.get('features'):
        geojson['features'][0]['properties']['userCanEdit'] = True
    geojson = json.dumps(geojson)

    def on_get(request, form_resource):
        form_resource = FormResourceGeoRef(instance=resource)
        if community:
            logger.debug('community_slug: {}'.format(community_slug))
            form_resource.fields['community'].widget = forms.HiddenInput()
            form_resource.initial['community'] = community.id
        form_resource.helper.form_action = reverse('edit_resource')

        return form_resource

    def on_after_save(request, obj):
        prefix = '/{}'.format(community_slug) if community_slug else ''
        _url = '{}/resource/{}'.format(prefix, obj.id)
        return {'redirect': _url}

    return {'on_get': on_get, 'on_after_save': on_after_save,
            'community': community, 'geojson': geojson, 'resource': resource}


def search_by_kind(request):
    logger.debug('acessing komoo_resource > search_by_kind')
    term = request.GET.get('term', '')
    kinds = ResourceKind.objects.filter(Q(name__icontains=term) |
        Q(slug__icontains=term))
    d = [{'value': k.id, 'label': k.name} for k in kinds]
    return HttpResponse(simplejson.dumps(d),
        mimetype="application/x-javascript")


def search_by_tag(request):
    logger.debug('acessing resource > search_by_tag')
    term = request.GET['term']
    qset = TaggedItem.tags_for(Resource).filter(name__istartswith=term
            ).annotate(count=Count('taggit_taggeditem_items__id')
            ).order_by('-count', 'slug')[:10]
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
                mimetype="application/x-javascript")


@render_to('komoo_map/show.html')
def show_on_map(request, geojson=''):
    resource = get_object_or_404(Resource, pk=request.GET.get('id', ''))
    geojson = create_geojson([resource])
    return dict(geojson=geojson)


@ajax_request
def resource_get_or_add_kind(request):
    term = request.POST.get('value', '')
    kinds = ResourceKind.objects.filter(Q(name__iexact=term) |
        Q(slug__iexact=term))
    if not kinds.count() and term:
        r = ResourceKind(name=term)
        r.save()
        obj = dict(added=True, id=r.id, value=r.name)
    else:
        obj = dict(added=False, id=None, value=term)
    return obj
