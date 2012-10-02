# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import json

from django.db.models.query_utils import Q
from django.shortcuts import HttpResponse, get_object_or_404, redirect
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.urlresolvers import reverse

from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from lib.taggit.models import TaggedItem
from ajaxforms import ajax_form

from komoo_resource.models import Resource, ResourceKind
from komoo_resource.forms import FormResource, FormResourceGeoRef
from main.utils import (create_geojson, paginated_query, sorted_query,
                        filtered_query)


logger = logging.getLogger(__name__)


def resources_to_resource(self):
    return redirect(reverse('resource_list'), permanent=True)


@render_to('resource/list.html')
def resource_list(request):
    sort_order = ['creation_date', 'votes', 'name']

    query_set = filtered_query(Resource.objects, request)

    resources_list = sorted_query(query_set, sort_order, request)
    resources_count = resources_list.count()
    resources = paginated_query(resources_list, request)

    return dict(resources=resources, resources_count=resources_count)


@render_to('resource/show.html')
def show(request, id=None):
    resource = get_object_or_404(Resource, pk=id)
    geojson = create_geojson([resource])
    similar = Resource.objects.filter(Q(kind=resource.kind) |
        Q(tags__in=resource.tags.all())).exclude(pk=resource.id).distinct()[:5]

    return dict(resource=resource, similar=similar, geojson=geojson)


@login_required
@ajax_form('resource/new.html', FormResource, 'form_resource')
def new_resource(request, *arg, **kwargs):
    def on_get(request, form_resource):
        form_resource.helper.form_action = reverse('new_resource')
        return form_resource

    def on_after_save(request, obj):
        return {'redirect': obj.view_url}

    return {'on_get': on_get, 'on_after_save': on_after_save}


@login_required
@ajax_form('resource/new_frommap.html', FormResourceGeoRef, 'form_resource')
def new_resource_from_map(request, *args, **kwargs):

    def on_get(request, form_resource):
        form_resource.helper.form_action = reverse('new_resource_from_map')
        return form_resource

    def on_after_save(request, obj):
        return {'redirect': obj.view_url}

    return {'on_get': on_get, 'on_after_save': on_after_save}


@login_required
@ajax_form('resource/edit.html', FormResourceGeoRef, 'form_resource')
def edit_resource(request, id='', *arg, **kwargs):
    resource = get_object_or_None(Resource, pk=id)
    geojson = create_geojson([resource], convert=False)

    if geojson and geojson.get('features'):
        geojson['features'][0]['properties']['userCanEdit'] = True
    geojson = json.dumps(geojson)

    def on_get(request, form):
        form = FormResourceGeoRef(instance=resource)
        form.helper.form_action = reverse('edit_resource',
                                          kwargs={'id': id})

        return form

    def on_after_save(request, obj):
        return {'redirect': obj.view_url}

    return {'on_get': on_get, 'on_after_save': on_after_save,
            'geojson': geojson, 'resource': resource}


def search_by_kind(request):
    term = request.GET.get('term', '')
    kinds = ResourceKind.objects.filter(Q(name__icontains=term) |
        Q(slug__icontains=term))
    d = [{'value': k.id, 'label': k.name} for k in kinds]
    return HttpResponse(simplejson.dumps(d),
        mimetype="application/x-javascript")


def search_tags(request):
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

