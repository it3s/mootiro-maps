#! coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.shortcuts import (render_to_response, RequestContext, 
        get_object_or_404)
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from lib.taggit.models import TaggedItem
from ajaxforms.forms import ajax_form
from annoying.decorators import render_to

from .forms import FormProject
from .models import Project

logger = logging.getLogger(__name__)


def project_list(request):
    #  TODO implement-me
    return {}


@render_to('project/view.html')
def project_view(request, project_slug=''):
    project = get_object_or_404(Project, slug=project_slug)
    return dict(project=project)


@login_required
@ajax_form('project/new.html', FormProject)
def project_new(request):
    logger.debug('acessing project > project_new')

    def on_get(request, form):
        form.helper.form_action = reverse('project_new')
        return form

    def on_after_save(request, project):
        redirect_url = project.view_url
        return {'redirect': redirect_url}

    return {'on_get': on_get, 'on_after_save': on_after_save}


def tag_search(request):
    logger.debug('acessing project > tag_search')
    term = request.GET['term']
    qset = TaggedItem.tags_for(Project).filter(name__istartswith=term)
    # qset = TaggedItem.tags_for(project)
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
                mimetype="application/x-javascript")


