#! coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response, RequestContext
from lib.taggit.models import TaggedItem

from .forms import FormProject
from .models import Project

def project_list(request):
    #  TODO implement-me
    return {}


def project_view(request, project_slug=''):
    # TODO implement-me
    return {}


def project_new(request, project_slug=''):
    form = FormProject()
    return render_to_response(
            'project/new.html',
            dict(form_project=form),
            context_instance=RequestContext(request))


def tag_search(request):
    logger.debug('acessing project > tag_search')
    term = request.GET['term']
    qset = TaggedItem.tags_for(Project).filter(name__istartswith=term)
    # qset = TaggedItem.tags_for(project)
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
                mimetype="application/x-javascript")


