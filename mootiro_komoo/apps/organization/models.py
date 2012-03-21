# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from komoo_map.models import GeoRefModel
from community.models import Community


class Organization(GeoRefModel):
    name = models.CharField(max_length=320)
    slug = models.SlugField(max_length=320)
    description = models.TextField(null=True, blank=True)

    creation_date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, null=True, blank=True)

    community = models.ForeignKey(Community, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Organization, self).save(*args, **kwargs)
