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
from django.core.urlresolvers import reverse
from django import forms
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
    if community_slug:
        logger.debug('community_slug: {}'.format(community_slug))
        community = get_object_or_404(Community, slug=community_slug)
        resources = Resource.objects.filter(community=community)
    else:
        community = None
        resources = Resource.objects.all()
    return dict(resources=resources, community=community)


@render_to('resource/show.html')
def show(request, id=None):
    logger.debug('acessing komoo_resource > show')
    resource = get_object_or_404(Resource, pk=id)
    geojson = create_geojson([resource])
    similar = Resource.objects.filter(Q(kind=resource.kind) |
        Q(tags__in=resource.tags.all())).exclude(pk=resource.id)[:5]
    return dict(resource=resource, similar=similar, geojson=geojson)


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

            if _id:
                return HttpResponseRedirect(reverse('view_resource', args=(resource.id,)))
            else:
                return render_to_response('resource/new.html',
                    dict(redirect=reverse('view_resource', args=(resource.id,))),
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
