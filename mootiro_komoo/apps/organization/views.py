# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import json

from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models.query_utils import Q
from django.utils import simplejson
from django.db.models import Count
from django.core.urlresolvers import reverse

from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from fileupload.models import UploadedFile
from lib.taggit.models import TaggedItem
from ajaxforms import ajax_form
from authentication.utils import login_required

from organization.models import Organization
from organization.forms import FormOrganization, FormOrganizationGeoRef
from main.utils import (paginated_query, create_geojson, sorted_query,
                        filtered_query, get_filter_params)

logger = logging.getLogger(__name__)


@render_to('organization/list.html')
def organization_list(request):
    org_sort_order = ['creation_date', 'name']

    filtered, filter_params = get_filter_params(request)

    query_set = filtered_query(Organization.objects, request)
    organizations_list = sorted_query(query_set, org_sort_order,
                                         request)
    organizations_count = organizations_list.count()
    organizations = paginated_query(organizations_list, request)
    return dict(organizations=organizations, filtered=filtered,
                organizations_count=organizations_count,
                filter_params=filter_params)


@render_to('organization/show.html')
def show(request, id=''):
    organization = get_object_or_404(Organization, pk=id)

    geojson = create_geojson([organization])
    files = UploadedFile.get_files_for(organization)
    if organization.logo_id:
        files = files.exclude(pk=organization.logo_id)

    return dict(organization=organization, geojson=geojson)


@render_to('organization/related_items.html')
def related_items(request, id=''):
    organization = get_object_or_None(Organization, pk=id) or Organization()
    geojson = create_geojson(organization.related_items)
    return {'organization': organization, 'geojson': geojson}


@login_required
@ajax_form('organization/new.html', FormOrganization, 'form_organization')
def new_organization(request, *arg, **kwargs):

    def on_get(request, form):
        form.helper.form_action = reverse('new_organization')
        return form

    def on_after_save(request, obj):
        return {'redirect': obj.view_url}

    return {'on_get': on_get, 'on_after_save': on_after_save}


@login_required
@ajax_form('organization/new_frommap.html', FormOrganizationGeoRef,
           'form_organization')
def new_organization_from_map(request, *arg, **kwargs):

    def on_get(request, form):
        form.helper.form_action = reverse('new_organization_from_map')
        return form

    def on_after_save(request, obj):
        return {'redirect': obj.view_url}

    return {'on_get': on_get, 'on_after_save': on_after_save}


@login_required
@ajax_form('organization/edit.html', FormOrganizationGeoRef,
           'form_organization')
def edit_organization(request, id='', *arg, **kwargs):
    organization = get_object_or_None(Organization, pk=id) or Organization()

    geojson = create_geojson([organization], convert=False)
    if geojson and geojson.get('features'):
        geojson['features'][0]['properties']['userCanEdit'] = True
    geojson = json.dumps(geojson)

    def on_get(request, form):
        form = FormOrganizationGeoRef(instance=organization)
        form.helper.form_action = reverse('edit_organization',
                                          kwargs={'id': organization.id})
        return form

    def on_after_save(request, obj):
        return {'redirect': reverse('view_organization',
                                    kwargs={'id': obj.id})}

    return {'on_get': on_get, 'on_after_save': on_after_save,
            'geojson': geojson, 'organization': organization}


def search_by_name(request):
    term = request.GET.get('term', '')
    orgs = Organization.objects.filter(Q(name__icontains=term) |
        Q(slug__icontains=term))
    d = [{'value': o.id, 'label': o.name} for o in orgs]
    return HttpResponse(simplejson.dumps(d),
        mimetype="application/x-javascript")


def search_tags(request):
    term = request.GET['term']
    qset = TaggedItem.tags_for(Organization).filter(name__istartswith=term
            ).annotate(count=Count('taggit_taggeditem_items__id')
            ).order_by('-count', 'slug')[:10]
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
                mimetype="application/x-javascript")
