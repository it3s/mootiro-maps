# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from komoo_map.models import GeoRefModel
from community.models import Community
from need.models import TargetAudience


class Organization(models.Model):
    name = models.CharField(max_length=320, unique=True)
    slug = models.SlugField(max_length=320)
    description = models.TextField(null=True, blank=True)

    creation_date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, null=True, blank=True)

    community = models.ManyToManyField(Community, null=True, blank=True)

    link = models.CharField(max_length=250, null=True, blank=True)
    contact = models.TextField(null=True, blank=True)

    categories = models.ManyToManyField('OrganizationCategory', null=True, blank=True)
    target_audiences = models.ManyToManyField(TargetAudience, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Organization, self).save(*args, **kwargs)

    image = "img/organization.png"
    image_off = "img/organization-off.png"


class OrganizationBranch(GeoRefModel):
    name = models.CharField(max_length=320, unique=True)
    slug = models.SlugField(max_length=320)

    organization = models.ForeignKey(Organization)
    info = models.TextField(null=True, blank=True)

    creation_date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(OrganizationBranch, self).save(*args, **kwargs)

    image = "img/organization.png"
    image_off = "img/organization-off.png"


class OrganizationCategory(models.Model):
    name = models.CharField(max_length=320, unique=True)
    slug = models.CharField(max_length=320, unique=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *a, **kw):
        self.slug = slugify(self.name)
        return super(OrganizationCategory, self).save(*a, **kw)


class OrganizationCategoryTranslation(models.Model):
    name = models.CharField(max_length=320)
    slug = models.CharField(max_length=320)
    lang = models.CharField(max_length=10)
    category = models.ForeignKey(OrganizationCategory)

    def __unicode__(self):
        return self.name

    def save(self, *a, **kw):
        self.slug = slugify(self.name)
        return super(OrganizationCategoryTranslation, self).save(*a, **kw)
