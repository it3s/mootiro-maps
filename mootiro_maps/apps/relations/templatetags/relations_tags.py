#! coding: utf-8 -*-
import json
from django import template
from relations.models import Relation

register = template.Library()

@register.inclusion_tag('relations/edit.html', takes_context=True)
def edit_relations_for(context, obj=None):
    options = Relation.rel_type_options()
    return {"options": options}

