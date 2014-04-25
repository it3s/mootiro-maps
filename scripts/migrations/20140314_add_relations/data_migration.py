# -*- coding: utf-8 -*-

from komoo_resource.models import Resource
from organization.models import Organization
from community.models import Community
from need.models import Need
from investment.models import Investment
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

def migrate_investments():
    for inv in Investment.objects.all():
        if not inv.investor.is_anonymous and inv.investor.content_object:
            oid = Relation.build_oid(inv.investor.content_object)
            relation = [{
                'target': Relation.build_oid(inv.grantee),
                'rel_type': 'investment',
                'direction': '+',
                'metadata': {
                    'start_date': inv.date.strftime('%d/%m/%Y') if inv.date else None,
                    'end_date': inv.end_date.strftime('%d/%m/%Y') if inv.end_date else None,
                    'description': inv.name,
                    'value': inv.value,
                }
            }]
            Relation.edit(oid, relation)


def run():
    migrate_community_relations()
    migrate_investments()

