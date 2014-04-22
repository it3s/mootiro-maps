# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import itertools
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


from main.mixins import BaseModel
from authentication.models import User
from organization.models import Organization
from komoo_resource.models import Resource
from need.models import Need
from community.models import Community
from komoo_project.models import Project
from proposal.models import Proposal
from investment.models import Investment

RELATION_TYPES = [
    ('ownership', 'Ownership'),
    ('participation', 'Participation'),
    ('partnership', 'Partnership'),
    ('grants', 'Grants'),
    ('certification', 'Certification'),
    ('students attendance', 'Students attendance'),
    ('directing people', 'Directing people'),
    ('volunteers', 'Volunteers'),
    ('support', 'Support'),
    ('representation', 'Representation'),
    ('membership', 'Membership'),
    ('supply', 'Supply'),
    ('council', 'Council'),
    ('contains', 'Contains'),
    ('investment', 'Investment'),
]

TABLE_ID_MAP = {
    'Organization': 'o',
    'Resource': 'r',
    'Need': 'n',
    'User': 'u',
    'Community': 'c',
    'Project': 'p',
    'Proposal': 's',
    'Investment': 'i',
}

def _get_model_class_for_oid(oid):
    return {
        'o': Organization,
        'r': Resource,
        'n': Need,
        'u': User,
        'c': Community,
        'p': Project,
        's': Proposal,
        'i': Investment,
    }[oid[0]]


def _rel_type_dict():
    return {
        # 'relation_type_name': (from_1_to_2, from_2_to_1),

        'ownership': (
            _('owns'), _('is owned by')
        ),
        # possui, pertence à

        'participation': (
            _('participates in'), _('has as participant')
        ),
        # participa de, tem como participante

        'partnership': (
            _('partners with'), _('partners with')
        ),
        # é parceiro de, é parceiro de

        'grants': (
            _('gives a grant to'), _('receives a grant from')
        ),
        # finacia, recebe um financiamento de

        'certification': (
            _('certifies'), _('is certified by')
        ),
        # certifica, é certificada por

        'students attendance': (
            _('attends students from'), _('attends')
        ),
        # students attendance, attends students from - atende alunos de

        'directing people': (
            _('directs people to'), _('receives people from')
        ),
        # encaminha atendidos para, recebe encaminhamentos de atendidos de

        'volunteers': (
            _('recruits volunteers for'), _('receives volunteers from')
        ),
        # recruta voluntários para, recebe voluntários de

        'support': (
            _('supports'), _('is supported by')
        ),
        # suporta, recebe suporte

        'representation': (
            _('represents'), _('is represented by')
        ),
        # representa, é representado por

        'membership': (
            _('is a member of'), _('has as member')
        ),
        # é membro de, tem como membro

        'supply': (
            _('supplies to'), _('buys from')
        ),
        # fornece para, compra de

        'council': (
            _('is board member of'), _('has as board member')
        ),
        # é conselheiro de, tem como conselheiro

        'contains': (
            _('contains'), _('belongs to')
        ),
        # contém, pertence a

        'investment': (
            _('invested in'), _('received investment from')
        ),
        # investiu em, recebeu investimento de
    }

def _swap_direction(direction):
    return {'+': '-', '-': '+'}[direction]


class RelationMetadata(BaseModel):
    value = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()


class Relation(BaseModel):
    """Generic relations"""
    oid_1 = models.CharField(max_length=64, null=False)
    oid_2 = models.CharField(max_length=64, null=False)
    rel_type = models.CharField(max_length=246, null=False, choices=RELATION_TYPES)
    direction = models.CharField(max_length=1, null=False, choices=[('+', '+'), ('-', '-')])
    metada = models.ForeignKey(RelationMetadata)

    # Meta info
    # creator = models.ForeignKey(User, editable=False, null=True,
    #                             related_name='created_resources')
    creation_date = models.DateTimeField(auto_now_add=True)
    # last_editor = models.ForeignKey(User, editable=False, null=True,
    #                                 blank=True)
    last_update = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"[relation :: %s]  %s => %s" % (self.rel_type, self.oid_1, self.oid_2)

    # ==========================================================================
    # Utils

    @classmethod
    def build_oid(cls, obj):
        return "{ref}{id}".format(
            ref=TABLE_ID_MAP[obj.__class__.__name__],
            id=obj.id)

    @classmethod
    def relations_for(cls, obj):
        oid = obj if isinstance(obj, basestring) else cls.build_oid(obj)
        relations = []
        for rel in cls.objects.filter(Q(oid_1=oid) | Q(oid_2=oid)):
            target_oid = rel.oid_1 if oid != rel.oid_1 else rel.oid_2
            direction = rel.direction if oid == rel.oid_1 else _swap_direction(rel.direction)
            relations.append({
                'target': cls.get_model_from_oid(target_oid),
                'target_oid': target_oid,
                'type': None,
                'direction': direction,
                'rel_type': rel.rel_type,
                'relation_title': cls.relation_title(rel.rel_type, direction),
                'metadata': None,
            })
        return relations

    @classmethod
    def edit(cls, obj_oid, relations):
        # delete removed relations
        old_relations_oids = map(lambda r: r['target_oid'], cls.relations_for(obj_oid))
        edited_relations_oids = map(lambda r: r['target'], relations)
        for oid in set(old_relations_oids) - set(edited_relations_oids):
            cls.get_relation(obj_oid, oid).delete()

        # add or update relations
        for rel in relations:
            oid_1, oid_2 = [obj_oid, rel['target']]
            relation = cls.get_relation(oid_1, oid_2)
            relation.rel_type = rel['rel_type']
            direction = rel['direction'] if oid_1 == relation.oid_1 else _swap_direction(rel['direction'])
            relation.direction = direction
            relation.save()

    @classmethod
    def get_relation(cls, oid_1, oid_2):
        qs = cls.objects.filter(
            (Q(oid_1=oid_1) & Q(oid_2=oid_2)) |
            (Q(oid_1=oid_2) & Q(oid_2=oid_1)) )
        return qs[0] if qs.exists() else Relation(oid_1=oid_1, oid_2=oid_2)

    @classmethod
    def get_model_from_oid(cls, oid):
        return _get_model_class_for_oid(oid).objects.get(pk=oid[1:])

    @classmethod
    def rel_type_options(cls):
        options = []
        for rel_type, relations in _rel_type_dict().iteritems():
            options.append({
                'type': rel_type,
                'direction': '+',
                'name': relations[0]
            })
            options.append({
                'type': rel_type,
                'direction': '-',
                'name': relations[1]
            })
        return options

    @classmethod
    def relation_title(cls, rel_type, direction):
        index = 0 if direction == '+' else 1
        return _rel_type_dict()[rel_type][index]

