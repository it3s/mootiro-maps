# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import json
import markdown

from django import forms
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.shortcuts import (render_to_response, RequestContext,
    get_object_or_404, HttpResponse)
from django.db.models.query_utils import Q
from django.utils import simplejson
from django.utils.html import escape
from django.db.models import Count
from django.core.urlresolvers import reverse

from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None
from fileupload.models import UploadedFile
from lib.taggit.models import TaggedItem
from ajaxforms import ajax_form


from organization.models import Organization, OrganizationBranch
from organization.forms import FormOrganization, FormBranch
from community.models import Community
from main.utils import (paginated_query, create_geojson, sorted_query,
                        filtered_query, fix_community_url)
from main.widgets import Autocomplete

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

    org_sort_order = ['creation_date', 'votes', 'name']

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


@login_required
@ajax_form('organization/new.html', FormOrganization, 'form_organization')
def new_organization(request, community_slug='', *arg, **kwargs):
    logger.debug('acessing organization > new_organization')
    community = get_object_or_None(Community, slug=community_slug)

    def on_get(request, form):
        if community:
            logger.debug('community_slug: {}'.format(community_slug))
            form.fields['community'].widget = forms.HiddenInput()
            form.initial['community'] = community.id
        if community_slug:
            form.helper.form_action = reverse('new_organization',
                    kwargs={'community_slug': community_slug})
        else:
            form.helper.form_action = reverse('new_organization')
        return form

    def on_after_save(request, obj):
        if community_slug:
            kwargs_ = {'organization_slug': obj.slug,
                      'community_slug': community_slug}
        else:
            kwargs_ = {'organization_slug': obj.slug}
        return {'redirect': reverse('view_organization', kwargs=kwargs_)}

    return {'on_get': on_get, 'on_after_save': on_after_save,
            'community': community}


@login_required
@render_to('organization/new_frommap.html')
def new_organization_from_map(request, community_slug='', *args, **kwargs):
    logger.debug('acessing organization > new_organization_from_map')
    community = get_object_or_None(Community, slug=community_slug)
    form_org = FormOrganization()
    form_org.helper.form_action = reverse('add_org_from_map')
    form_branch = FormBranch(auto_id='id_branch_%s')
    form_branch.helper.form_action = reverse('add_branch_from_map')
    form_branch.fields['geometry'].widget.attrs['id'] = 'id_geometry'
    org_name_widget = Autocomplete(Organization,
        "/organization/search_by_name", clean_on_change=False).render('org_name')
    return {'community': community, 'form_org': form_org,
            'form_branch': form_branch, 'org_name_widget': org_name_widget}


@login_required
@ajax_form('organization/edit.html', FormOrganization, 'form_organization')
def edit_organization(request, community_slug='', organization_slug='',
                      *arg, **kwargs):
    logger.debug('acessing organization > edit_organization')
    community = get_object_or_None(Community, slug=community_slug)
    organization = get_object_or_None(Organization, pk=request.GET.get('id', 0))

    geojson = create_geojson([organization], convert=False)
    if geojson and geojson.get('features'):
        geojson['features'][0]['properties']['userCanEdit'] = True
    geojson = json.dumps(geojson)

    def on_get(request, form):
        form = FormOrganization(instance=organization)
        if community:
            logger.debug('community_slug: {}'.format(community_slug))
            form.fields['community'].widget = forms.HiddenInput()
            form.initial['community'] = community.id
        if community_slug:
            form.helper.form_action = reverse('edit_organization',
                    kwargs={'community_slug': community_slug})
        else:
            form.helper.form_action = reverse('edit_organization')
        return form

    def on_after_save(request, obj):
        if community_slug:
            kwargs_ = {'organization_slug': obj.slug,
                      'community_slug': community_slug}
        else:
            kwargs_ = {'organization_slug': obj.slug}
        return {'redirect': reverse('view_organization', kwargs=kwargs_)}

    return {'on_get': on_get, 'on_after_save': on_after_save,
            'community': community, 'geojson': geojson,
            'organization': organization}


@login_required
@ajax_form(form_class=FormBranch)
def add_branch_from_map(request):
    logger.debug('acessing organization > add_branch_from_map')
    print '\n\nPOST DATA: %s\n\n' % request.POST
    return {'here?': True}


@login_required
@ajax_form(form_class=FormOrganization)
def add_org_from_map(request):
    logger.debug('acessing organization > add_org_from_map')
    return {}


@ajax_request
def edit_inline_branch(request):
    logger.debug('acessing organization > edit_inline_branch: POST={}'.format(
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

        communities = request.POST.get('branch_community',
            '').rstrip('|').lstrip('|').split('|')
        branch.save()

        if communities:
            branch.community.clear()
            for comm in communities:
                if comm:
                    branch.community.add(comm)
        branch.save()
        communities = render_to_response(
            'organization/branch_communities_list.html', {'branch': branch},
            context_instance=RequestContext(request)).content

        success = True
    else:
        success, info, name = False, '', ''
    return dict(success=success, info=info, name=name, communities=communities)


@ajax_request
def verify_org_name(request):
    name = request.POST.get('org_name', '')
    q = Organization.objects.filter(
            Q(name__iexact=name) | Q(slug=slugify(name))
        )
    if q.count():
        r_dict = {'exists': True, 'id': q[0].id, 'slug': q[0].slug}
    else:
        r_dict = {'exists': False}
    return r_dict


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
