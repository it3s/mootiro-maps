# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import json
import markdown

from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (render_to_response, RequestContext,
    get_object_or_404, HttpResponseRedirect, HttpResponse)
from django.db.models.query_utils import Q
from django.utils import simplejson
from django.utils.html import escape

from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None

from organization.models import Organization, OrganizationBranch
from organization.forms import FormOrganizationNew, FormBranchNew, \
                               FormOrganizationEdit
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
    branches = organization.organizationbranch_set.all()
    geojson = create_geojson(branches)
    community = get_object_or_None(Community, slug=community_slug)

    return dict(organization=organization, geojson=geojson,
                community=community)


class New(View):
    """Class based view for adding a Organization"""

    @method_decorator(login_required)
    def get(self, request, community_slug=None, *args, **kwargs):
        logger.debug('acessing organization > Edit with GET')
        community = get_object_or_None(Community, slug=community_slug)

        form_org = FormOrganizationNew()
        form_branch = FormBranchNew()

        if request.GET.get('frommap', None) == 'false':
            form_branch.fields.pop('geometry', '')
            tmplt = 'organization/new.html'
        else:
            tmplt = 'organization/new_frommap.html'

        return render_to_response(tmplt,
            dict(form_org=form_org, form_branch=form_branch, community=community),
            context_instance=RequestContext(request))

    def post(self, request, community_slug=None, *args, **kwargs):
        logger.debug('acessing organization > Edit with POST: {}'.format(
            request.POST))

        form_control = request.POST.get('form_control', '').split('|')

        form_org = FormOrganizationNew(request.POST)
        form_branch = FormBranchNew(request.POST)
        community = get_object_or_None(Community, slug=community_slug)

        if request.GET.get('frommap', None) == 'false':
            form_branch.fields.pop('geometry', '')

        org_is_valid = not 'organization' in form_control or form_org.is_valid()
        branch_is_valid = not 'branch' in form_control or form_branch.is_valid()

        if org_is_valid and branch_is_valid:
            if 'organization' in form_control:
                organization = form_org.save(user=request.user)
            else:
                organization = Organization.objects.get(pk=request.POST.get('org_name'))
            if 'branch' in form_control:
                form_branch.save(user=request.user, organization=organization)

            prefix = '/{}'.format(community_slug) if community_slug else ''
            _url = '{}/organization/{}'.format(prefix, organization.slug)
            return render_to_response('organization/new_frommap.html',
                dict(redirect=_url, form_org=form_org, form_branch=form_branch,
                     community=community),
                context_instance=RequestContext(request))
        else:
            logger.debug('Form erros: {}'.format(dict(form_org._errors
                            ).update(dict(form_branch._errors))))
            return render_to_response('organization/new.html',
                dict(form_org=form_org, form_branch=form_branch,
                     community=community),
                context_instance=RequestContext(request))


class Edit(View):
    """Class based view for editing a Organization"""

    @method_decorator(login_required)
    def get(self, request, community_slug=None, *args, **kwargs):
        logger.debug('acessing organization > Edit with GET')
        community = get_object_or_None(Community, slug=community_slug)

        _id = request.GET.get('id', None)
        if _id:
            organization = get_object_or_404(Organization, pk=_id)

            form_org = FormOrganizationEdit(instance=organization)
            geojson = create_geojson([organization], convert=False)
            if geojson and geojson.get('features'):
                geojson['features'][0]['properties']['userCanEdit'] = True
            geojson = json.dumps(geojson)
        else:
            form_org = FormOrganizationEdit()
            organization = Organization()
            geojson = '{}'

        tmplt = 'organization/edit.html'
        return render_to_response(tmplt,
            dict(form_org=form_org, community=community,
                 organization=organization, geojson=geojson),
            context_instance=RequestContext(request))

    def post(self, request, community_slug=None, *args, **kwargs):
        logger.debug('acessing organization > Edit with POST: {}'.format(
            request.POST))
        _id = request.POST.get('id', None)

        if _id:
            organization = get_object_or_404(Organization,
                pk=request.POST['id'])
            form_org = FormOrganizationEdit(request.POST, instance=organization)
        else:
            form_org = FormOrganizationEdit(request.POST)

        community = get_object_or_None(Community, slug=community_slug)

        if form_org.is_valid():
            organization = form_org.save(user=request.user)

            geojson = create_geojson([organization], convert=False)
            if geojson and geojson.get('features'):
                geojson['features'][0]['properties']['userCanEdit'] = True
            geojson = json.dumps(geojson)

            prefix = '/{}'.format(community_slug) if community_slug else ''
            _url = '{}/organization/{}'.format(prefix, organization.slug)
            if _id:
                return HttpResponseRedirect(_url)
            else:
                return render_to_response('organization/edit.html',
                    dict(redirect=_url, community=community, geojson=geojson,
                         organization=organization),
                    context_instance=RequestContext(request))
        else:
            logger.debug('Form erros: {}'.format(dict(form_org._errors)))
            tmplt = 'organization/edit.html'
            return render_to_response(tmplt,
                dict(form_org=form_org, community=community, geojson='{}'),
                context_instance=RequestContext(request))


@ajax_request
def branch_edit(request):
    logger.debug('acessing organization > branch_edit: POST={}'.format(
            request.POST))

    if request.POST.get('id', None) and request.POST.get('info', None):
        branch = get_object_or_404(OrganizationBranch, pk=request.POST.get('id', ''))
        branch.info = escape(request.POST['info'])
        info = markdown.markdown(escape(request.POST['info']))
        branch.save()
        success = True
    else:
        success, info = False, ''
    return dict(success=success, info=info)


def search_by_name(request):
    logger.debug('acessing organization > search_by_name')
    term = request.GET.get('term', '')
    orgs = Organization.objects.filter(Q(name__icontains=term) |
        Q(slug__icontains=term))
    d = [{'value': o.id, 'label': o.name} for o in orgs]
    return HttpResponse(simplejson.dumps(d),
        mimetype="application/x-javascript")
