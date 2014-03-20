#! coding: utf-8 -*-
import json
from django import template

register = template.Library()

@register.inclusion_tag('relations/edit.html', takes_context=True)
def projects_for_object(context, obj=None):
    return {}

