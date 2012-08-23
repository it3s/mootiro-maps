#! coding: utf-8 -*-
from django import template
from django.contrib.contenttypes.models import ContentType
from komoo_project.models import Project, ProjectRelatedObject
from main.widgets import Autocomplete


register = template.Library()


@register.filter
def user_can_edit_this_project(project, user):
    return project.user_can_edit(user)


@register.inclusion_tag('project/projects_tag.html', takes_context=True)
def projects_for_object(context, obj):
    ct = ContentType.objects.get_for_model(obj)
    projects = [p.project for p in
        ProjectRelatedObject.objects.filter(content_type=ct, object_id=obj.id)]
    project_widget = Autocomplete(Project, '/project/search_by_name')
    project_widget = "%s \n %s" % (str(project_widget.media),
                                     project_widget.render('project'))
    return dict(projects=projects, project_widget=project_widget,
                contenttype=ct.id, object_id=obj.id)

