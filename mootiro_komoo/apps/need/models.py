#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

import reversion
from lib.taggit.managers import TaggableManager

from community.models import Community
from main.utils import slugify
from komoo_map.models import GeoRefModel, POLYGON, LINESTRING, POINT
from vote.models import VotableModel


class NeedCategory(models.Model):
    name = models.CharField(max_length=64, blank=False)

    # Adding categories to be translated.
    # Probably there is a better way to do this.
    categories = [
        _('Culture'),
        _('Education'),
        _('Environment'),
        _('Health'),
        _('Housing'),
        _('Local Economy'),
        _('Mobility'),
        _('Social Service'),
        _('Sport'),
        _('Security'),
    ]

    def __unicode__(self):
        return unicode(self.name)

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


class Need(GeoRefModel, VotableModel):
    """A need of a Community"""

    class Meta:
        verbose_name = "need"
        verbose_name_plural = "needs"

    title = models.CharField(max_length=256, blank=False)
    # Auto-generated url slug. It's not editable via ModelForm.
    slug = models.CharField(max_length=256, blank=False, db_index=True)
    description = models.TextField()

    # Meta info
    creator = models.ForeignKey(User, editable=False, null=True, related_name='created_needs')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_editor = models.ForeignKey(User, editable=False, null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)

    # Relationships
    # community = models.ForeignKey(Community, related_name="needs", null=True, blank=True)
    community = models.ManyToManyField(Community, related_name="needs", null=True, blank=True)
    categories = models.ManyToManyField(NeedCategory)
    target_audiences = models.ManyToManyField(TargetAudience, blank=False)

    tags = TaggableManager()

    class Map:
        title = _('Need')
        editable = True
        background_color =  '#f42c5e'
        border_color = '#d31e52'
        geometries = (POLYGON, LINESTRING, POINT)
        categories = [
            ('Culture'),
            ('Education'),
            ('Environment'),
            ('Health'),
            ('Housing'),
            ('Local Economy'),
            ('Mobility'),
            ('Social Service'),
            ('Sport'),
            ('Security'),
        ]
        form_view_name = 'new_need_from_map'
        form_view_kwargs = {}

    def __unicode__(self):
        return unicode(self.title)

    ### Needed to slugify items ###
    def slug_exists(self, slug):
        """Answers if a given slug is valid in the needs namespace of the
        community.
        """
        return Need.objects.filter(slug=slug).exists()

    def save(self, *args, **kwargs):
        old_title = Need.objects.get(id=self.id).title if self.id else None
        if not self.id or old_title != self.title:
            self.slug = slugify(self.title, self.slug_exists)
        return super(Need, self).save(*args, **kwargs)
    ### END ###

    image = "img/need.png"
    image_off = "img/need-off.png"

    # Url aliases
    @property
    def home_url_params(self):
        return {'id': self.id}

    @property
    def view_url(self):
        return reverse('view_need', kwargs=self.home_url_params)

    @property
    def edit_url(self):
        return reverse('edit_need', kwargs=self.home_url_params)

    @property
    def admin_url(self):
        return reverse('admin:{}_{}_change'.format(self._meta.app_label,
            self._meta.module_name), args=[self.id])

    @property
    def name(self):
        return self.title

    @property
    def perm_id(self):
        return 'n%d' % self.id


if not reversion.is_registered(Need):
    reversion.register(Need)
