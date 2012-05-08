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

from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None
from lib.taggit.models import TaggedItem
from ajaxforms import ajax_form

from komoo_resource.models import Resource, ResourceKind
from komoo_resource.forms import FormResource
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


@ajax_form('resource/new.html', FormResource)
def new_resource(request):
    return {}


class New(View):
    """ Class based view for editing a Resource """

    @method_decorator(login_required)
    def get(self, request, community_slug=None, *args, **kwargs):
        logger.debug('acessing komoo_resource > New with GET')
        community = get_object_or_None(Community, slug=community_slug)

        form_resource = FormResource()
        form_resource.fields['name'].initial = ''
        form_resource.fields.pop('image', '')

        if request.GET.get('frommap', None) == 'false':
            form_resource.fields.pop('geometry', '')
            tmplt = 'resource/new.html'
        else:
            tmplt = 'resource/new_frommap.html'

        if community:
            logger.debug('community_slug: {}'.format(community_slug))
            form_resource.fields['community'].widget = forms.HiddenInput()
            form_resource.initial['community'] = community.id

        return render_to_response(tmplt,
            dict(form_resource=form_resource, community=community),
            context_instance=RequestContext(request))

    def post(self, request, community_slug=None, *args, **kwargs):
        logger.debug('acessing komoo_resource > New with POST : {}'.format(
                        request.POST))

        form_resource = FormResource(request.POST)
        community = get_object_or_None(Community, slug=community_slug)

        if request.GET.get('frommap', None) == 'false':
            form_resource.fields.pop('geometry', '')
            tmplt = 'resource/new.html'
        else:
            tmplt = 'resource/new_frommap.html'

        if form_resource.is_valid():
            resource = form_resource.save(user=request.user)

            prefix = '/{}'.format(community_slug) if community_slug else ''
            _url = '{}/resource/{}'.format(prefix, resource.id)
            return render_to_response('resource/new_frommap.html',
                dict(redirect=_url, form_resource=form_resource,
                     community=community),
                context_instance=RequestContext(request))
        else:
            logger.debug('Form erros: {}'.format(dict(form_resource._errors)))
            return render_to_response(tmplt,
                dict(form_resource=form_resource, community=community),
                context_instance=RequestContext(request))


class Edit(View):
    """ Class based view for editing a Resource """

    @method_decorator(login_required)
    def get(self, request, community_slug=None, *args, **kwargs):
        logger.debug('acessing komoo_resource > Edit with GET')
        community = get_object_or_None(Community, slug=community_slug)

        _id = request.GET.get('id', None)
        if _id:
            resource = get_object_or_404(Resource, pk=_id)
            form_resource = FormResource(instance=resource)
        else:
            resource = None
            form_resource = FormResource()
            form_resource.fields.pop('image', '')

        if community:
            form_resource.fields['community'].widget = forms.HiddenInput()
            form_resource.initial['community'] = community.id

        geojson = create_geojson([resource], convert=False)
        if geojson and geojson.get('features'):
            geojson['features'][0]['properties']['userCanEdit'] = True
        geojson = json.dumps(geojson)

        return render_to_response('resource/edit.html',
            dict(form_resource=form_resource, community=community,
                resource=resource, geojson=geojson),
            context_instance=RequestContext(request))

    def post(self, request, community_slug=None, *args, **kwargs):
        logger.debug('acessing komoo_resource > Edit with POST\n'
                     'POST : {}\nFILES : {}'.format(request.POST, request.FILES))
        _id = request.POST.get('id', None)
        # if _id:
        resource = get_object_or_404(Resource, pk=request.POST['id'])
        form_resource = FormResource(request.POST, request.FILES, instance=resource)
        # else:
        #     form_resource = FormResource(request.POST, request.FILES)

        community = get_object_or_None(Community, slug=community_slug)

        if form_resource.is_valid():
            resource = form_resource.save(user=request.user)

            prefix = '/{}'.format(community_slug) if community_slug else ''
            _url = '{}/resource/{}'.format(prefix, resource.id)
            if _id:
                return HttpResponseRedirect(_url)
            else:
                return render_to_response('resource/edit.html',
                    dict(redirect=_url, community=community),
                    context_instance=RequestContext(request))
        else:
            logger.debug('Form erros: {}'.format(dict(form_resource._errors)))

            geojson = create_geojson([resource], convert=False)
            if geojson and geojson.get('features'):
                geojson['features'][0]['properties']['userCanEdit'] = True
            geojson = json.dumps(geojson)

            return render_to_response('resource/edit.html',
                dict(form_resource=form_resource, community=community,
                     geojson=geojson, resource=resource),
                context_instance=RequestContext(request))


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
