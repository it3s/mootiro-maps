#! coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import simplejson

from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from lib.taggit.models import TaggedItem
from ajaxforms.forms import ajax_form
from annoying.decorators import render_to, ajax_request
from main.utils import (paginated_query, sorted_query, filtered_query,
        create_geojson, to_json)
from main.tasks import send_explanations_mail

from authentication.utils import login_required
from model_versioning.tasks import versionate

from .forms import FormProject
from .models import Project, ProjectRelatedObject

from organization.models import Organization
from need.models import Need
from komoo_resource.models import Resource
from community.models import Community
from investment.models import Investment

logger = logging.getLogger(__name__)

CLASSNAME_MAP = {
    "organization": Organization,
    "need":         Need,
    "resource":     Resource,
    "community":    Community,
    "investment":   Investment,
}

@render_to('project/list.html')
def project_list(request):
    sort_order = ['creation_date', 'name']
    query_set = filtered_query(Project.objects, request)
    projects_list = sorted_query(query_set, sort_order, request)
    projects_count = projects_list.count()
    projects = paginated_query(projects_list, request)
    return dict(projects=projects, projects_count=projects_count)


@render_to('project/view.html')
def project_view(request, id=''):
    project = get_object_or_404(Project, pk=id)

    proj_objects, items = {}, []

    proj_objects['User'] = {'app_name': 'authentication', 'objects_list': []}

    for c in project.all_contributors:
        proj_objects['User']['objects_list'].append({
            'name': c.name,
            'link': c.view_url,
            'avatar': c.avatar,
            'id': c.id,
            'has_geojson': bool(getattr(c, 'geometry', ''))
        })

    for p in project.related_objects:
        obj = p.content_object
        if obj:
            if not proj_objects.get(obj.__class__.__name__, None):
                proj_objects[obj.__class__.__name__] = {
                        'app_name': obj.__module__.split('.')[0],
                        'objects_list': []}
            proj_objects[obj.__class__.__name__]['objects_list'].append({
                'name': obj.name.strip(),
                'link': obj.view_url,
                'id': obj.id,
                'has_geojson': bool(getattr(obj, 'geometry', ''))
            })

            if not obj.is_empty():
                items.append(obj)
    geojson = create_geojson(items)

    # ugly sort
    for key in proj_objects.iterkeys():
        proj_objects[key]['objects_list'].sort(key=lambda o: o['name'])

    return dict(project=project, geojson=geojson, proj_objects=proj_objects,
                user_can_discuss=project.user_can_discuss(request.user))


@render_to('project/related_items.html')
def project_map(request, id=''):
    project = get_object_or_404(Project, pk=id)
    related_items = []

    for obj in project.related_items:
        if obj and not obj.is_empty():
            related_items.append({'name': getattr(obj, 'name', _('Unnamed')), 'obj': obj})

    related_items.sort(key=lambda o: o['name'])
    related_items = [o['obj'] for o in related_items]

    geojson = create_geojson(related_items)
    return dict(project=project, geojson=geojson)


@login_required
@ajax_form('project/edit.html', FormProject)
def project_new(request):

    def on_get(request, form):
        form.helper.form_action = reverse('project_new')
        return form

    def on_after_save(request, project):
        send_explanations_mail(project.creator, 'project')
        # Add the project creator as contributor
        project.contributors.add(project.creator)
        versionate(request.user, project)
        return {'redirect': project.view_url}

    return {'on_get': on_get, 'on_after_save': on_after_save, 'project': None}


@login_required
@ajax_form('project/edit.html', FormProject)
def project_edit(request, id='', *arg, **kwargs):
    project = get_object_or_404(Project, pk=id)

    layers = to_json(project.layers)

    if not project.user_can_edit(request.user):
        return redirect(project.view_url)

    def on_get(request, form):
        form = FormProject(instance=project)
        form.helper.form_action = reverse('project_edit',
                                          kwargs={'id': project.id})
        return form

    def on_after_save(request, obj):
        # add user who edited as contributor.
        obj.contributors.add(request.user)
        versionate(request.user, obj)
        return {'redirect': obj.view_url}

    return {'on_get': on_get, 'on_after_save': on_after_save,
            'project': project, 'layers': layers}


@ajax_request
def add_related_object(request):
    ct = request.POST.get('content_type', '')
    obj_id = request.POST.get('object_id', '')
    proj_id = request.POST.get('project_id', '')
    proj = get_object_or_404(Project, pk=proj_id)

    if proj and obj_id and ct:
        obj = ContentType.objects.get(id=ct).get_object_for_this_type(id=obj_id)
        if obj:
            proj.save_related_object(obj, request.user)
            return {'success': True,
                    'project': {
                        'id': proj.id,
                        'name': proj.name,
                        'link': proj.view_url
                    }}

    return {'success': False}

class _FakeFilterRequest:
    def __init__(self, params):
        self.GET = params

@ajax_request
def add_list_of_objects(request):
    project = Project.objects.get(pk=request.POST['project_id'])

    klass = CLASSNAME_MAP[request.POST['object_type']]
    filter_params = simplejson.loads(request.POST['filter_params'])
    object_list = filtered_query(klass.objects, _FakeFilterRequest(filter_params))

    for obj in object_list:
        project.save_related_object(obj, request.user)

    return {'success': True, 'redirect_url': project.view_url}


@login_required
@ajax_request
def delete_relations(request):
    logger.debug('POST: {}'.format(request.POST))
    project = request.POST.get('project', '')
    relations = request.POST.get('associations', '')

    project = get_object_or_404(Project, pk=project)

    if not project.user_can_edit(request.user):
        return redirect(project.view_url)
    try:
        for rel in relations.split('|'):
            if rel:
                p = ProjectRelatedObject.objects.get(pk=rel)
                p.delete()
        success = True
    except Exception as err:
        logger.error('ERRO ao deletar relacao: %s' % err)
        success = False

    return{'success': success}


@login_required
@ajax_request
def save_layers(request, id=None):
    proj = get_object_or_404(Project, pk=id)
    print 'proj = ', proj

    layers = request.POST.get('layers', None)
    print 'layers = ', layers

    if proj and layers:
        proj.layers = simplejson.loads(layers)
        return {'success': True, 'redirect_url': proj.view_url}

    return {'success': False}


def tag_search(request):
    term = request.GET['term']
    qset = TaggedItem.tags_for(Project).filter(name__istartswith=term)
    # qset = TaggedItem.tags_for(project)
    tags = [t.name for t in qset]
    return HttpResponse(to_json(tags),
                mimetype="application/x-javascript")


def search_by_name(request):
    term = request.GET['term']
    projects = Project.objects.filter(Q(name__icontains=term) |
                                           Q(slug__icontains=term))
    d = [{'value': p.id, 'label': p.name} for p in projects
            if p.user_can_edit(request.user)]
    return HttpResponse(to_json(d),
            mimetype="application/x-javascript")


@render_to('project/explanations.org.html')
def explanations(request):
    name = request.GET.get('name', request.user.name)
    return {'name': name}
