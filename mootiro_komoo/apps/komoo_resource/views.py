# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.views.generic import View
from django.db.models.query_utils import Q
from django.shortcuts import (render_to_response, RequestContext, HttpResponse,
        HttpResponseRedirect, get_object_or_404)
from django.utils import simplejson
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django import forms
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from taggit.models import TaggedItem

from komoo_resource.models import Resource, ResourceKind
from komoo_resource.forms import FormResource
from main.utils import create_geojson
from community.models import Community


logger = logging.getLogger(__name__)


@render_to('resource/list.html')
def resource_list(request, community_slug=''):
    logger.debug('acessing komoo_resource > list')
    page = request.GET.get('page', '')
    size = request.GET.get('size', 10)

    if community_slug:
        logger.debug('community_slug: {}'.format(community_slug))
        community = get_object_or_404(Community, slug=community_slug)
        resources_list = Resource.objects.filter(community=community)
    else:
        community = None
        resources_list = Resource.objects.all()

    paginator = Paginator(resources_list, size)
    try:
        resources = paginator.page(page)
    except PageNotAnInteger:  # If page is not an integer, deliver first page.
        resources = paginator.page(1)
    except EmptyPage:  # If page is out of range, deliver last page
        resources = paginator.page(paginator.num_pages)

    return dict(resources=resources, community=community)


@render_to('resource/show.html')
def show(request, community_slug=None, id=None):
    logger.debug('acessing komoo_resource > show')
    resource = get_object_or_404(Resource, pk=id)
    geojson = create_geojson([resource])
    similar = Resource.objects.filter(Q(kind=resource.kind) |
        Q(tags__in=resource.tags.all())).exclude(pk=resource.id).distinct()[:5]
    community = get_object_or_None(Community, slug=community_slug)
    return dict(resource=resource, similar=similar, geojson=geojson,
                community=community)


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
            form_resource = FormResource()

        if community:
            print 'fields->community:\n%s' % dir(form_resource.fields['community'])
            form_resource.fields['community'].widget = forms.HiddenInput()
            form_resource.initial['community'] = community.id

        tmplt = 'resource/edit.html' if _id else 'resource/new.html'
        return render_to_response(tmplt,
            dict(form_resource=form_resource, community=community),
            context_instance=RequestContext(request))

    def post(self, request, community_slug=None, *args, **kwargs):
        logger.debug('acessing komoo_resource > Edit with POST\n'
                     'request : {}'.format(request.POST))
        _id = request.POST.get('id', None)
        if _id:
            resource = get_object_or_404(Resource, pk=request.POST['id'])
            form_resource = FormResource(request.POST, instance=resource)
        else:
            form_resource = FormResource(request.POST)

        community = get_object_or_None(Community, slug=community_slug)

        if form_resource.is_valid():
            resource = form_resource.save(user=request.user)

            prefix = '/{}'.format(community_slug) if community_slug else ''
            _url = '{}/resource/{}'.format(prefix, resource.id)
            if _id:
                return HttpResponseRedirect(_url)
            else:
                return render_to_response('resource/new.html',
                    dict(redirect=_url),
                    context_instance=RequestContext(request))
        else:
            logger.debug('Form erros: {}'.format(dict(form_resource.__errors)))
            tmplt = 'resource/edit.html' if _id else 'resource/new.html'
            return render_to_response(tmplt,
                dict(form_resource=form_resource, community=community),
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
    qset = TaggedItem.tags_for(Resource).filter(name__istartswith=term)
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
                mimetype="application/x-javascript")
