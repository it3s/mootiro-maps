#! coding: utf-8 -*-
import json
from django import template
from main.utils import to_json
from relations.models import Relation

register = template.Library()

@register.inclusion_tag('relations/edit.html', takes_context=True)
def edit_relations_for(context, obj=None):
    options = Relation.rel_type_options()
    relations = [  # XXX fake data for testing
        {"direction":"-","rel_type":"students attendance","target_oid":"r1277", "target_name": "ABC Rugby"},
        {"direction":"-","rel_type":"directing people","target":"o15639", "target_name": "Sesc Santo Amaro"}
    ]
    return {"options": options, "relations": to_json(relations)}

