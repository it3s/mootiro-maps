# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import os
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import reversion
from taggit.managers import TaggableManager
from community.models import Community
from komoo_map.models import GeoRefModel


# def resource_upload(instance, filename):
#     ext = filename[filename.rindex('.'):]
#     return os.path.join('resource', '{fname}{ext}'.format(
#                             fname=int(time.time() * 1000), ext=ext))


class ResourceKind(models.Model):
    """Kind of Resources"""
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(ResourceKind, self).save(*args, **kwargs)


class Resource(GeoRefModel):
    """Resources model"""
    name = models.CharField(max_length=256)
    creator = models.ForeignKey(User, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    kind = models.ForeignKey(ResourceKind)
    description = models.TextField()
    # image = models.FileField(upload_to=resource_upload, null=True, blank=True)
    community = models.ForeignKey(Community, related_name='resources',
        null=True, blank=True)
    tags = TaggableManager()


reversion.register(Resource)
