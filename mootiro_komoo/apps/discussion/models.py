# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse

import reversion


class Discussion(models.Model):
    text = models.TextField(null=True, blank=True)

    @property
    def content_object (self):
        return self.content_objects.all()[0]

    # Meta info
    last_editor = models.ForeignKey(User, editable=False, null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "discussion"
        verbose_name_plural = "discussions"


if not reversion.is_registered(Discussion):
    reversion.register(Discussion)
