# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.gis.db import models
from django.contrib.auth.models import User
import reversion

RESOURCE_CHOICES = [

]
_resource_dict = dict(RESOURCE_CHOICES)


class ResourceKind(models.Model):
    """Kind of Resources"""
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name


class Resource(models.Model):
    """Resources model"""
    name = models.CharField(max_length=256)
    creator = models.ForeignKey(User, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    kind = models.ForeignKey(ResourceKind)
    description = models.TextField()
    location = models.GeometryCollectionField(null=True, blank=True)

    objects = models.GeoManager()

reversion.register(Resource)
