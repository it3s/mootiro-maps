#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

import reversion
from lib.taggit.managers import TaggableManager

from community.models import Community
from main.utils import slugify
from komoo_map.models import GeoRefModel


class NeedCategory(models.Model):
    name = models.CharField(max_length=64, blank=False)

    # Adding categories to be translated.
    # Probably there are a better way to do this.
    _('Culture')
    _('Education')
    _('Environment')
    _('Health')
    _('Housing')
    _('Local Economy')
    _('Mobility')
    _('Social Service')
    _('Sport')

    def __unicode__(self):
        return self.name

    @classmethod
    def get_image(cls, name):
        return "need_categories/%s.png" % slugify(name)

    @classmethod
    def get_image_off(cls, name):
        return "need_categories/%s-off.png" % slugify(name)

    @property
    def image(self):
        return self.get_image(self.name)

    @property
    def image_off(self):
        return self.get_image_off(self.name)


class TargetAudience(models.Model):
    name = models.CharField(max_length=64, unique=True, blank=False)

    def __unicode__(self):
        return self.name


class Need(GeoRefModel):
    """A need of a Community"""

    title = models.CharField(max_length=256, blank=False, db_index=True)
    # Auto-generated url slug. It's not editable via ModelForm.
    slug = models.CharField(max_length=256, unique=True, blank=False, db_index=True)
    description = models.TextField(db_index=True)

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

    def __unicode__(self):
        return unicode(self.title)

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

    image = "img/need.png"
    image_off = "img/need-off.png"

reversion.register(Need)
