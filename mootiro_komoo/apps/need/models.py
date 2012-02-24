#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.db import models

from taggit.managers import TaggableManager
#from taggit.models import TaggedItemBase

from community.models import Community
from main.utils import slugify


class NeedCategory(models.Model):
    name = models.CharField(max_length=64, blank=False)

    def __unicode__(self):
        return self.name


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

    # Relationships
    community = models.ForeignKey(Community, related_name="needs")
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
        # FIXME: always changing the name
        old_title = Need.objects.get(id=self.id).title if self.id else None
        if not self.id or old_title != self.title:
            self.slug = slugify(self.title, self.slug_exists)
        super(Need, self).save(*args, **kwargs)
    ### END ###
