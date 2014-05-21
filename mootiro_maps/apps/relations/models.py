# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import itertools
from datetime import datetime
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
    ('attendance', 'Attendance'),
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

        'attendance': (
            _('attended by'), _('attends')
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


class Relation(BaseModel):
    """Generic relations"""
    oid_1 = models.CharField(max_length=64, null=False)
    oid_2 = models.CharField(max_length=64, null=False)
    rel_type = models.CharField(max_length=246, null=False, choices=RELATION_TYPES)
    direction = models.CharField(max_length=1, null=False, choices=[('+', '+'), ('-', '-')])

    # Meta info
    # creator = models.ForeignKey(User, editable=False, null=True,
    #                             related_name='created_resources')
    creation_date = models.DateTimeField(auto_now_add=True)
    # last_editor = models.ForeignKey(User, editable=False, null=True,
    #                                 blank=True)
    last_update = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"[relation :: %s]  %s => %s" % (self.rel_type, self.oid_1, self.oid_2)

    def upsert_metadata(self, data, parse=False):
        if parse:
            if data['start_date']:
                data['start_date'] = datetime.strptime(data['start_date'], "%d/%m/%Y").date()
            if data['end_date']:
                data['end_date'] = datetime.strptime(data['end_date'], "%d/%m/%Y").date()
            if data['value']:
                data['value'] = float(data['value'])

        metadata, created = self.metadata.get_or_create()
        metadata.from_dict(data)
        metadata.save()

    def metadata_dict(self):
        try:
            return self.metadata.get().to_dict()
        except:
            return {}

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
                'id': rel.id,
                'target': cls.get_model_from_oid(target_oid),
                'target_oid': target_oid,
                'direction': direction,
                'rel_type': rel.rel_type,
                'relation_title': cls.relation_title(rel.rel_type, direction),
                'metadata': rel.metadata_dict(),
            })
        return relations

    @classmethod
    def edit(cls, obj_oid, relations):
        # delete removed relations
        old_relations_ids = map(lambda r: r['id'], cls.relations_for(obj_oid))
        edited_relations_ids = [int(r['id']) for r in relations if r.get('id', None)]
        relations_to_delete =  set(old_relations_ids) - set(edited_relations_ids)
        cls.objects.filter(pk__in=relations_to_delete).delete()

        # add or update relations
        for rel in relations:
            oid_1, oid_2 = [obj_oid, rel['target']]

            # get existing relation or create new one
            relation = cls.objects.get(pk=int(rel['id'])) if rel.get('id', None) else Relation(oid_1=oid_1, oid_2=oid_2)

            if relation.has_changed(oid_1, oid_2):
                relation.oid_1 = oid_1
                relation.oid_2 = oid_2

            # old
            relation.rel_type = rel['rel_type']
            direction = rel['direction'] if oid_1 == relation.oid_1 else _swap_direction(rel['direction'])
            relation.direction = direction
            relation.save()
            if rel.get('metadata', None):
                relation.upsert_metadata(rel['metadata'], parse=True)

    # @classmethod
    # def get_relation(cls, oid_1, oid_2):
    #     qs = cls.objects.filter(
    #         (Q(oid_1=oid_1) & Q(oid_2=oid_2)) |
    #         (Q(oid_1=oid_2) & Q(oid_2=oid_1)) )
    #     return qs[0] if qs.exists() else Relation(oid_1=oid_1, oid_2=oid_2)

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


    def has_changed(self, oid_1, oid_2):
        return not (
            (self.oid_1 == oid_1 and self.oid_2 == oid_2)
            or
            (self.oid_1 == oid_2 and elf.oid_2 == oid_1)
        )


class RelationMetadata(BaseModel):

    CURRENCIES_CHOICES = (
        ('BRL', _('Brazilian Real (BRL)')),
        ('USD', _('US-Dollar (USD)')),
        ('EUR', _('Euro')),
    )

    currency = models.CharField(max_length=3, choices=CURRENCIES_CHOICES,
                null=True, blank=True)
    value = models.FloatField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    description = models.TextField(null=True)
    relation = models.ForeignKey(Relation, related_name="metadata")

    def to_dict(self):
        return {
            'description': self.description,
            'start_date': self.start_date.strftime('%d/%m/%Y') if self.start_date else None,
            'end_date': self.end_date.strftime('%d/%m/%Y') if self.end_date else None,
            'value': self.value
        }

    def from_dict(self, d):
        self.description = d.get('description', None)
        self.start_date = d.get('start_date', None)
        self.end_date = d.get('end_date', None)
        self.value = d.get('value', None)


