#! coding: utf-8 -*-
import json
from django import template
from main.utils import to_json
from relations.models import Relation

register = template.Library()

@register.inclusion_tag('relations/edit.html', takes_context=True)
def edit_relations_for(context, obj=None):
    options = Relation.rel_type_options()
    relations = [
        {
            "direction": rel['direction'],
            "rel_type": rel['rel_type'],
            "target_oid": rel['target_oid'],
            "target_name": rel['target'].name
        }
        for rel in Relation.relations_for(obj)]
    oid = Relation.build_oid(obj)
    return {"options": options, "relations": to_json(relations), "oid": oid}


@register.inclusion_tag('relations/view.html', takes_context=True)
def view_relations_for(context, obj=None):
    relations = [
            {
                'name': rel['target'].name,
                'rel_type': rel['relation_title'],
                'link': rel['target'].view_url
            }
            for rel in Relation.relations_for(obj)]

    return {"relations": relations}


