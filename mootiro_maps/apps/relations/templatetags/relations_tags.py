#! coding: utf-8 -*-
import json
from django import template

register = template.Library()

@register.inclusion_tag('relations/edit.html', takes_context=True)
def edit_relations_for(context, obj=None):
    return {}

