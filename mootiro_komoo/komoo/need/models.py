#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.db import models

from taggit.managers import TaggableManager

from komoo.community.models import Community
from komoo.utils import slugify


class NeedCategory(models.Model):
    name = models.CharField(max_length=64, blank=False)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'komoo'  # needed for Django to find the model


class Need(models.Model):
    AUDIENCE_CHOICES = (
        ('CHL', '0-12'),
        ('TEN', '12-18'),
        ('MIN', 'Minorities'),
    )

    title = models.CharField(max_length=256, blank=False)
    # Auto-generated url slug. It's not editable via ModelForm.
    slug = models.SlugField(max_length=256, unique=True,
                            editable=False, blank=False)
    description = models.TextField()
    target_audience = models.CharField(max_length=3, choices=AUDIENCE_CHOICES)

    # Relationships
    community = models.ForeignKey(Community, related_name="needs")
    categories = models.ManyToManyField(NeedCategory)

    tags = TaggableManager()

    class Meta:
        app_label = 'komoo'  # needed for Django to find the model

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
