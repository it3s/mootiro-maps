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
            "id": rel['id'],
            "direction": rel['direction'],
            "rel_type": rel['rel_type'],
            "target_oid": rel['target_oid'],
            "target_name": rel['target'].name,
            "metadata": rel['metadata']
        }
        for rel in Relation.relations_for(obj)]
    oid = Relation.build_oid(obj)
    return {"options": options, "relations": to_json(relations), "oid": oid}

def _dict_has_values(d):
    return reduce(lambda x, acc: x or acc,  map(bool, d.values()), False)

@register.inclusion_tag('relations/view.html', takes_context=True)
def view_relations_for(context, obj=None):
    relations = [
            {
                'name': rel['target'].name,
                'rel_type': rel['relation_title'],
                'link': rel['target'].view_url,
                'metadata': rel['metadata'] if _dict_has_values(rel['metadata']) else {}
            }
            for rel in Relation.relations_for(obj)]

    return {"relations": relations}


