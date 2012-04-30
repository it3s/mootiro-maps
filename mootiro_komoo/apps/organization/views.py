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
from django.db.models import Count
from django.core.urlresolvers import reverse

from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None
from fileupload.models import UploadedFile
from lib.taggit.models import TaggedItem


from organization.models import Organization, OrganizationBranch
from organization.forms import FormOrganizationNew, FormBranchNew, \
                               FormOrganizationEdit
from community.models import Community
from main.utils import (paginated_query, create_geojson, sorted_query,
                        filtered_query, fix_community_url)

logger = logging.getLogger(__name__)


def prepare_organization_objects(community_slug="", organization_slug=""):
    """Retrieves a tuple (organization, community). According to given
    parameters may raise an 404. Creates a new organization if organization_slug
    is evaluated as false."""
    community = get_object_or_None(Community, slug=community_slug)
    if organization_slug:
        filters = dict(slug=organization_slug)
        if community:
            filters["community"] = community
        organization = get_object_or_404(Organization, **filters)
    else:
        organization = Organization(community=community)
    return organization, community


@render_to('organization/list.html')
@fix_community_url('organization_list')
def organization_list(request, community_slug=''):
    logging.debug('acessing organization > list')

    org_sort_order = ['creation_date', 'name']

    if community_slug:
        logger.debug('community_slug: {}'.format(community_slug))
        community = get_object_or_None(Community, slug=community_slug)
        query_set = community.organization_set
    else:
        community = None
        query_set = Organization.objects

    query_set = filtered_query(query_set, request)
    organizations_list = sorted_query(query_set, org_sort_order,
                                         request)
    organizations_count = organizations_list.count()
    organizations = paginated_query(organizations_list, request)
    return dict(community=community, organizations=organizations,
                organizations_count=organizations_count)


@render_to('organization/show.html')
def show(request, organization_slug='', community_slug=''):
    logger.debug('acessing organization > show')

    organization = get_object_or_404(Organization, slug=organization_slug)
    branches = organization.organizationbranch_set.all().order_by('name')
    geojson = create_geojson(branches)
    community = get_object_or_None(Community, slug=community_slug)
    files = UploadedFile.get_files_for(organization)
    if organization.logo_id:
        files = files.exclude(pk=organization.logo_id)
    photos = paginated_query(files, request, size=3)

    return dict(organization=organization, geojson=geojson,
                community=community, photos=photos)


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
            if form_org and form_org._errors:
                logger.debug('Form Org errors: {}'.format(
                                                    dict(form_org._errors)))
            if form_branch and form_branch._errors:
                logger.debug('Form Org errors: {}'.format(
                                                    dict(form_branch._errors)))
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
                dict(form_org=form_org, community=community, geojson='{}',
                     organization=organization),
                context_instance=RequestContext(request))


@ajax_request
def branch_edit(request):
    logger.debug('acessing organization > branch_edit: POST={}'.format(
            request.POST))

    if request.POST.get('id', None):
        branch = get_object_or_404(OrganizationBranch, pk=request.POST.get('id', ''))
        branch.info = escape(request.POST['info'])
        name = escape(request.POST.get('name', ''))
        if name:
            branch.name = name
        geometry = request.POST.get('geometry', '')
        if geometry:
            branch.geometry = geometry
        info = markdown.markdown(escape(request.POST['info']))
        branch.save()
        success = True
    else:
        success, info, name = False, '', ''
    return dict(success=success, info=info, name=name)


def search_by_name(request):
    logger.debug('acessing organization > search_by_name')
    term = request.GET.get('term', '')
    orgs = Organization.objects.filter(Q(name__icontains=term) |
        Q(slug__icontains=term))
    d = [{'value': o.id, 'label': o.name} for o in orgs]
    return HttpResponse(simplejson.dumps(d),
        mimetype="application/x-javascript")


def search_by_tag(request):
    logger.debug('acessing organization > search_by_tag')
    term = request.GET['term']
    qset = TaggedItem.tags_for(Organization).filter(name__istartswith=term
            ).annotate(count=Count('taggit_taggeditem_items__id')
            ).order_by('-count', 'slug')[:10]
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
                mimetype="application/x-javascript")
