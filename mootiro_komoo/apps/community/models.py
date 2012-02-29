#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.contrib.gis.db import models
from main.utils import slugify


class Community(models.Model):
    name = models.CharField(max_length=256, blank=False)
    # Auto-generated url slug. It's not editable via ModelForm.
    slug = models.SlugField(max_length=256, editable=False, blank=False)
    population = models.IntegerField(null=True, blank=True)  # number of inhabitants
    description = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    # Geolocalization attributes
    objects = models.GeoManager()
    geometry = models.PolygonField(srid=4326)

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
