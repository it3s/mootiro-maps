# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


class Organization(models.Model):
    name = models.CharField(max_length=320)
    slug = models.SlugField(max_length=320)
    description = models.TextField(null=True, blank=True)

    creation_date = models.DateTimeField(auto_add_now=True)
    creator = models.ForeignKey(User, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(*args, **kwargs)
