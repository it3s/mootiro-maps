#! coding: utf-8 -*-
from django import template

register = template.Library()

@register.filter
def user_can_edit_this_project(project, user):
    return project.user_can_edit(user)

