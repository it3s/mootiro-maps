#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.gis.db import models
from django.contrib.gis.measure import Distance
from django.contrib.auth.models import User

import reversion
from main.utils import slugify
from lib.taggit.managers import TaggableManager
from komoo_map.models import GeoRefModel
from vote.models import VotableModel


class Community(GeoRefModel, VotableModel):
    name = models.CharField(max_length=256, blank=False, db_index=True)
    # Auto-generated url slug. It's not editable via ModelForm.
    slug = models.SlugField(max_length=256, blank=False, db_index=True)
    population = models.IntegerField(null=True, blank=True)  # number of inhabitants
    description = models.TextField(null=True, blank=True, db_index=True)

    # Meta info
    creator = models.ForeignKey(User, editable=False, null=True, blank=True,
                        related_name='created_communities')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    tags = TaggableManager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "community"
        verbose_name_plural = "communities"

    ### Needed to slugify items ###
    def slug_exists(self, slug):
        """Answers if a given slug is valid in the communities namespace."""
        return Community.objects.filter(slug=slug).exists()

    def save(self, *args, **kwargs):
        old_name = Community.objects.get(id=self.id).name if self.id else None
        if not self.id or old_name != self.name:
            self.slug = slugify(self.name, self.slug_exists)
        super(Community, self).save(*args, **kwargs)
    ### END ###

    image = "img/community.png"
    image_off = "img/community-off.png"

    # TODO: order communities from the database
    def closest_communities(self, max=3, radius=Distance(km=25)):
        center = self.geometry.centroid
        unordered = Community.objects.filter(polys__distance_lte=(center, radius))
        closest = sorted(unordered, key=lambda c: c.geometry.distance(center))
        return closest[1:(max + 1)]

if not reversion.is_registered(Community):
    reversion.register(Community)
