#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import re
from django.db import models
from django.template.defaultfilters import slugify


class Community(models.Model):
    _name = models.CharField(max_length=256)
    # Auto-generated url slug. It's not editable via ModelForm.
    slug = models.SlugField(max_length=256, editable=False, blank=False)

    population = models.IntegerField()  # number of inhabitants
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    address = models.CharField(max_length=1024)

    class Meta:
        app_label = 'komoo'  # needed for Django to find the model
        verbose_name = "community"
        verbose_name_plural = "communities"

    name_has_changed = False
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self.name_has_changed = True
        self._name = name

    def set_slug(self):
        original = slugify(self.name)
        s = original
        n = 2
        while Community.objects.filter(slug=s).exists():
            s = re.sub(r'\d+$', '', s)  # removes trailing '-number'
            s = original + '-' + str(n)
            n += 1
        self.slug = s

    def save(self, *args, **kwargs):
        print self.name_has_changed
        if self.name_has_changed or not self.id:
            self.set_slug()
        super(Community, self).save(*args, **kwargs)
        self.name_has_changed = False
