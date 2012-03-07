#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.contrib.gis.db import models
from django.contrib.auth.models import User

import reversion
from taggit.managers import TaggableManager

from community.models import Community
from main.utils import slugify
from mootiro_komoo.lib.collection_from import CollectionFrom


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


class Need(models.Model):
    """A need of a Community"""

    title = models.CharField(max_length=256, blank=False)
    # Auto-generated url slug. It's not editable via ModelForm.
    slug = models.CharField(max_length=256, unique=True, editable=False, blank=False)
    description = models.TextField()

    # Meta info
    creator = models.ForeignKey(User, editable=False, related_name='created_needs')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    # Relationships
    community = models.ForeignKey(Community, related_name="needs", null=True, blank=True)
    categories = models.ManyToManyField(NeedCategory)
    target_audiences = models.ManyToManyField(TargetAudience, blank=False)

    tags = TaggableManager()

    # Geolocalization attributes
    objects = models.GeoManager()

    points = models.MultiPointField(null=True, blank=True, editable=False)
    lines = models.MultiLineStringField(null=True, blank=True, editable=False)
    polys = models.MultiPolygonField(null=True, blank=True, editable=False)
    geometry = CollectionFrom(points='points', lines='lines', polys='polys')

    ### Needed to slugify items ###
    def slug_exists(self, slug):
        """Answers if a given slug is valid in the needs namespace of the
        community.
        """
        return Need.objects.filter(community=self.community, slug=slug).exists()

    def save(self, *args, **kwargs):
        print "00000000000"
        old_title = Need.objects.get(id=self.id).title if self.id else None
        if not self.id or old_title != self.title:
            self.slug = slugify(self.title, self.slug_exists)
        print "11111111111"
        super(Need, self).save(*args, **kwargs)
        print "22222222222"
    ### END ###

reversion.register(Need)
