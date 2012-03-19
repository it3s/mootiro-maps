# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import reversion
from taggit.managers import TaggableManager
from community.models import Community
from komoo_map.models import GeoRefModel
from fileupload.models import UploadedFile


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
    community = models.ForeignKey(Community, related_name='resources',
        null=True, blank=True)
    tags = TaggableManager()

    def files_set(self):
        """ pseudo-reverse query for retrieving Resource Files"""
        return UploadedFile.get_files_for(self)

    def __unicode__(self):
        return unicode(self.name)


reversion.register(Resource)
