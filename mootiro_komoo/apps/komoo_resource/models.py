# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
import reversion

RESOURCE_CHOICES = [
    (1, 'Veículo'),
    (2, 'Equipamento'),
    (3, 'Espaço'),
    (4, 'Material Esportivo'),
    (5, 'Material Educacional'),
    (6, 'Outros'),
]
_resource_dict = dict(RESOURCE_CHOICES)


class Resource(models.Model):
    """Resources model"""
    name = models.CharField(max_length=256)
    creator = models.ForeignKey(User, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    kind = models.IntegerField(choices=RESOURCE_CHOICES)
    description = models.TextField()
    # location ?

    def kind_repr(self):
        return _resource_dict[self.kind]

reversion.register(Resource)
