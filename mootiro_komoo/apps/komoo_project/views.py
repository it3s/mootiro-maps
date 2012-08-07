#! coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils import simplejson

from lib.taggit.models import TaggedItem
from ajaxforms.forms import ajax_form
from annoying.decorators import render_to
from main.utils import paginated_query, sorted_query, filtered_query

from .forms import FormProject
from .models import Project

logger = logging.getLogger(__name__)


@render_to('project/list.html')
def project_list(request):
    logger.debug('acessing komoo_project > list')

    sort_order = ['creation_date', 'votes', 'name']

    community = None
    query_set = Project.objects

    query_set = filtered_query(query_set, request)

    projects_list = sorted_query(query_set, sort_order, request)
    projects_count = projects_list.count()
    projects = paginated_query(projects_list, request)

    return dict(projects=projects, community=community,
                projects_count=projects_count)


@render_to('project/view.html')
def project_view(request, project_slug=''):
    project = get_object_or_404(Project, slug=project_slug)
    return dict(project=project, geojson={})


@login_required
@ajax_form('project/edit.html', FormProject)
def project_new(request):
    logger.debug('acessing project > project_new')

    def on_get(request, form):
        form.helper.form_action = reverse('project_new')
        return form

    def on_after_save(request, project):
        return {'redirect': project.view_url}

    return {'on_get': on_get, 'on_after_save': on_after_save}


@login_required
@ajax_form('project/edit.html', FormProject)
def project_edit(request, project_slug='', *arg, **kwargs):
    logger.debug('acessing komoo_project > edit_project')

    project = get_object_or_404(Project, slug=project_slug)

    def on_get(request, form):
        form = FormProject(instance=project)
        kwargs = dict(project_slug=project_slug)
        form.helper.form_action = reverse('project_edit', kwargs=kwargs)

        return form

    def on_after_save(request, obj):
        return {'redirect': obj.view_url}

    return {'on_get': on_get, 'on_after_save': on_after_save,
            'project': project}


def tag_search(request):
    logger.debug('acessing project > tag_search')
    term = request.GET['term']
    qset = TaggedItem.tags_for(Project).filter(name__istartswith=term)
    # qset = TaggedItem.tags_for(project)
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
                mimetype="application/x-javascript")


