#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.db import models

from lib.taggit.managers import TaggableManager
from lib.taggit.models import TaggedItemBase

from community.models import Community
from main.utils import slugify


class NeedCategory(models.Model):
    name = models.CharField(max_length=64, blank=False)

    def __unicode__(self):
        return self.name 


class NeedTargetAudienceTag(TaggedItemBase):
    content_object = models.ForeignKey('Need')


class Need(models.Model):
    """A need of a Community"""

    title = models.CharField(max_length=256, blank=False)
    # Auto-generated url slug. It's not editable via ModelForm.
    slug = models.CharField(max_length=256, unique=True, editable=False, blank=False)
    description = models.TextField()

    # Relationships
    community = models.ForeignKey(Community, related_name="needs")
    categories = models.ManyToManyField(NeedCategory)

    tags = TaggableManager(related_name='need_tags')
    #target_audience = TaggableManager(verbose_name="Target audience",
    #    related_name="target_audience", through=NeedTargetAudienceTag)

    ### Needed to slugify items ###
    def slug_exists(self, slug):
        """Answers if a given slug is valid in the needs namespace of the
        community.
        """
        return Need.objects.filter(community=self.community, slug=slug).exists()

    def save(self, *args, **kwargs):
        old_title = Need.objects.get(id=self.id) if self.id else None
        if not self.id or old_title != self.title:
            self.slug = slugify(self.title, self.slug_exists)
        super(Need, self).save(*args, **kwargs)
    ### END ###
