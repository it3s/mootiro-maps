# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


from main.mixins import BaseModel
from authentication.models import User

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
]

TABLE_ID_MAP = {
    'Organization': 'o',
    'Resource': 'r',
    'Need': 'n',
    'User': 'u',
    'Community': 'c',
    'Project': 'p',
    'Proposal': 's',
}


class Relation(BaseModel):
    """Generic relations"""
    oid_1 = models.CharField(max_length=64, null=False)
    oid_2 = models.CharField(max_length=64, null=False)
    rel_type = models.CharField(max_length=246, null=False, choices=RELATION_TYPES)
    direction = models.CharField(max_length=1, null=False, choices=[('+', '+'), ('-', '-')])
    # metada = ??

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

    # def from_dict(self, data):
    #     keys = ['id', 'name', 'contact', 'geojson',  'creation_date',
    #             'is_admin', 'is_active', 'about_me']
    #     date_keys = ['creation_date']
    #     build_obj_from_dict(self, data, keys, date_keys)

    # def to_dict(self):
    #     fields_and_defaults = [
    #         ('name', None), ('kind_id', None), ('description', None),
    #         ('short_description ', None),
    #         ('creator_id', None), ('creation_date', None),
    #         ('last_editor_id', None), ('last_update', None),
    #         ('geojson', {}), ('contacts', {}),
    #     ]
    #     dict_ = {v[0]: getattr(self, v[0], v[1]) for v in fields_and_defaults}
    #     dict_['community'] = [comm.id for comm in self.community.all()]
    #     dict_['tags'] = [tag.name for tag in self.tags.all()]
    #     return dict_

    # def is_valid(self, ignore=[]):
    #     self.errors = {}
    #     valid = True
    #     return valid

    @classmethod
    def build_oid(cls, obj):
        return "{ref}{id}".format(
            ref=TABLE_ID_MAP[obj.__class__.__name__],
            id=obj.id)

    def relation_type(self):
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
        }[self.rel_type]
