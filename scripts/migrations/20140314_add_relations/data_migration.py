# -*- coding: utf-8 -*-

from komoo_resource.models import Resource
from organization.models import Organization
from community.models import Community
from need.models import Need
from relations.models import Relation

def migrate_community_relations():
    for model in [Resource, Organization, Need]:
        for obj in model.objects.all():
            if obj.community.count() > 0:
                obj_oid = Relation.build_oid(obj)
                relations = [
                    {
                        'target': 'c{id}'.format(id=comm.id),
                        'rel_type': 'contains',
                        'direction': '-',
                    } for comm in obj.community.all()
                ]
                if relations:
                    Relation.edit(obj_oid, relations)

def run():
    migrate_community_relations()


