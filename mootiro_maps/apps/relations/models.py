# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


from main.mixins import BaseModel
from authentication.models import User

# RELATION_TYPES = []

class Relation(BaseModel):
    """Generic relations"""
    pass
    # object_1 = models.CharField(max_lenght=64, null=False)
    # object_2 = models.CharField(max_lenght=64, null=False)
    # type = models.CharField(max_lenght=246, null=False, choices=RELATION_TYPES)
    # direction = models.CharField(max_lenght=1, null=False, choices=['+', '-'])
    # metada = ??

    # Meta info
    # creator = models.ForeignKey(User, editable=False, null=True,
    #                             related_name='created_resources')
    # creation_date = models.DateTimeField(auto_now_add=True)
    # last_editor = models.ForeignKey(User, editable=False, null=True,
    #                                 blank=True)
    # last_update = models.DateTimeField(auto_now=True)

    # def __unicode__(self):
    #     return unicode(self.name)


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
