#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.db import models
from django.template.defaultfilters import slugify

import re


class Community(models.Model):
    _name = models.CharField(max_length=256)
    # Auto-generated url slug. It's not editable via ModelForm.
    _slug = models.SlugField(max_length=256, editable=False, blank=False)

    population = models.IntegerField()  # number of inhabitants
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    address = models.CharField(max_length=1024)

    class Meta:
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

    @property
    def slug(self):
        return self._slug

    def set_slug(self):
        original = slugify(self.name)
        s = original
        n = 2
        while Community.objects.filter(_slug=s).exists():
            s = re.sub(r'\d+$', '', s)  # removes trailing '-number'
            s = original + '-' + str(n)
            n += 1
        self._slug = s

    def save (self, *args, **kwargs):
        print self.name_has_changed
        if self.name_has_changed or not self.id:
            self.set_slug()
        super(Community, self).save(*args, **kwargs)
        self.name_has_changed = False
