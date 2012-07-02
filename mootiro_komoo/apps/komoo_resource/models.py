# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from django.core.urlresolvers import reverse

import reversion
from lib.taggit.managers import TaggableManager

from community.models import Community
from komoo_map.models import GeoRefModel, POLYGON, LINESTRING, POINT
from investment.models import Investment
from fileupload.models import UploadedFile
from vote.models import VotableModel


class ResourceKind(models.Model):
    """Kind of Resources"""
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(ResourceKind, self).save(*args, **kwargs)

    @classmethod
    def favorites(cls, number=10):
        return ResourceKind.objects.all(
            ).exclude(name='').annotate(count=Count('resource__id')
            ).order_by('-count', 'slug')[:number]


class Resource(GeoRefModel, VotableModel):
    """Resources model"""
    name = models.CharField(max_length=256, default=_('Resource without name'))
    # slug = models.CharField(max_length=256, blank=False, db_index=True)
    creator = models.ForeignKey(User, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    kind = models.ForeignKey(ResourceKind, null=True, blank=True)
    description = models.TextField()
    contact = models.TextField(null=True, blank=True)
    community = models.ManyToManyField(Community, related_name='resources',
            null=True, blank=True)
    tags = TaggableManager()

    investments = generic.GenericRelation(Investment,
                        content_type_field='grantee_content_type',
                        object_id_field='grantee_object_id')

    class Map:
        editable = True
        background_color =  '#009fe3'
        border_color = '#0282af'
        geometries = (POLYGON, LINESTRING, POINT)

    def __unicode__(self):
        return unicode(self.name)

    ### Needed to slugify items ###
    # def slug_exists(self, slug):
    #     """Answers if a given slug is valid in the needs namespace of the
    #     community.
    #     """
    #     return Resource.objects.filter(slug=slug).exists()

    # def save(self, *args, **kwargs):
    #     old_name = Resource.objects.get(id=self.id).name if self.id else None
    #     if not self.id or old_name != self.name:
    #         self.slug = slugify(self.name, self.slug_exists)
    #     return super(Resource, self).save(*args, **kwargs)
    ### END ###

    image = "img/resource.png"
    image_off = "img/resource-off.png"

    def files_set(self):
        """ pseudo-reverse query for retrieving Resource Files"""
        return UploadedFile.get_files_for(self)

    @property
    def home_url_params(self):
        d = dict(resource_id=self.id)
        return d

    @property
    def view_url(self):
        return reverse('view_resource', kwargs=self.home_url_params)

    @property
    def edit_url(self):
        return reverse('edit_resource', kwargs=self.home_url_params)

    @property
    def admin_url(self):
        return reverse('admin:{}_{}_change'.format(self._meta.app_label,
            self._meta.module_name), args=[self.id])

    @property
    def new_investment_url(self):
        return reverse('new_investment', kwargs=self.home_url_params)

if not reversion.is_registered(Resource):
    reversion.register(Resource)
