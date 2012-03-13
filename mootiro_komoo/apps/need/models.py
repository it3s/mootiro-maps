#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.contrib.gis.db import models
from django.contrib.auth.models import User

import reversion
from taggit.managers import TaggableManager

from community.models import Community
from main.utils import slugify
from komoo_map.models import GeoRefModel


class NeedCategory(models.Model):
    name = models.CharField(max_length=64, blank=False)

    def __unicode__(self):
        return self.name

    @classmethod
    def get_image_tick(cls, name):
        print slugify.__doc__
        return "%s-tick.png" % slugify(name)

    @classmethod
    def get_image_no_tick(cls, name):
        return "%s-no-tick.png" % slugify(name)

    def image(self):
        return self.get_image_tick(self.name)


class TargetAudience(models.Model):
    name = models.CharField(max_length=64, unique=True, blank=False)

    def __unicode__(self):
        return self.name


class Need(GeoRefModel):
    """A need of a Community"""

    title = models.CharField(max_length=256, blank=False)
    # Auto-generated url slug. It's not editable via ModelForm.
    slug = models.CharField(max_length=256, unique=True, editable=False, blank=False)
    description = models.TextField()

    # Meta info
    creator = models.ForeignKey(User, editable=False, null=True, blank=True,
                related_name='created_needs')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    # Relationships
    community = models.ForeignKey(Community, related_name="needs", null=True, blank=True)
    categories = models.ManyToManyField(NeedCategory)
    target_audiences = models.ManyToManyField(TargetAudience, blank=False)

    tags = TaggableManager()

    ### Needed to slugify items ###
    def slug_exists(self, slug):
        """Answers if a given slug is valid in the needs namespace of the
        community.
        """
        return Need.objects.filter(community=self.community, slug=slug).exists()

    def save(self, *args, **kwargs):
        old_title = Need.objects.get(id=self.id).title if self.id else None
        if not self.id or old_title != self.title:
            self.slug = slugify(self.title, self.slug_exists)
        super(Need, self).save(*args, **kwargs)
    ### END ###

reversion.register(Need)
