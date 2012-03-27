# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import json

from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (render_to_response, RequestContext,
    get_object_or_404, HttpResponseRedirect)

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from organization.models import Organization
from organization.forms import FormOrganization
from community.models import Community
from main.utils import paginated_query, create_geojson

logger = logging.getLogger(__name__)


@render_to('organization/list.html')
def organization_list(request, community_slug=''):
    logging.debug('acessing organization > list')

    if community_slug:
        logger.debug('community_slug: {}'.format(community_slug))
        community = get_object_or_None(Community, slug=community_slug)
        organizations_list = community.organization_set.all()
    else:
        community = None
        organizations_list = Organization.objects.all()

    organizations = paginated_query(organizations_list, request)
    return dict(community=community, organizations=organizations)


@render_to('organization/show.html')
def show(request, organization_slug='', community_slug=''):
    logger.debug('acessing organization > show')

    organization = get_object_or_404(Organization, slug=organization_slug)
    geojson = create_geojson([organization])
    community = get_object_or_None(Community, slug=community_slug)

    return dict(organization=organization, geojson=geojson,
                community=community)


class Edit(View):
    """Class based view for editing a Organization"""

    @method_decorator(login_required)
    def get(self, request, community_slug=None, *args, **kwargs):
        logger.debug('acessing organization > Edit with GET')
        community = get_object_or_None(Community, slug=community_slug)

        _id = request.GET.get('id', None)
        if _id:
            organization = get_object_or_404(Organization, pk=_id)

            form_org = FormOrganization(instance=organization)
            geojson = create_geojson([organization], convert=False)
            geojson['features'][0]['properties']['userCanEdit'] = True
            geojson = json.dumps(geojson)
        else:
            form_org = FormOrganization()
            geojson = '{}'

        # form_org.initial['community'] = form_org.initial.get('community', [])
        # if community and not community.id in form_org.initial['community']:
            # form_org.initial['community'].append(community.id)

        tmplt = 'organization/edit.html' if _id else 'organization/new.html'
        return render_to_response(tmplt,
            dict(form_org=form_org, community=community, geojson=geojson),
            context_instance=RequestContext(request))

    def post(self, request, community_slug=None, *args, **kwargs):
        logger.debug('acessing organization > Edit with POST: {}'.format(
            request.POST))
        _id = request.POST.get('id', None)

        if _id:
            organization = get_object_or_404(Organization,
                pk=request.POST['id'])
            form_org = FormOrganization(request.POST, instance=organization)
        else:
            form_org = FormOrganization(request.POST)

        community = get_object_or_None(Community, slug=community_slug)

        if form_org.is_valid():
            organization = form_org.save(user=request.user)

            prefix = '/{}'.format(community_slug) if community_slug else ''
            _url = '{}/organization/{}'.format(prefix, organization.slug)
            if _id:
                return HttpResponseRedirect(_url)
            else:
                return render_to_response('organization/new.html',
                    dict(redirect=_url, community=community),
                    context_instance=RequestContext(request))
        else:
            logger.debug('Form erros: {}'.format(dict(form_org._errors)))
            tmplt = 'organization/edit.html' if _id else 'organization/new.html'
            return render_to_response(tmplt,
                dict(form_org=form_org, community=community),
                context_instance=RequestContext(request))
