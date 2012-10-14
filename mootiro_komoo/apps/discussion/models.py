# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse

from komoo_user.models import User

import reversion


class Discussion(models.Model):
    text = models.TextField(null=True, blank=True)

    content_type = models.ForeignKey(ContentType,  null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # Meta info
    last_editor = models.ForeignKey(User, editable=False, null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "discussion"
        verbose_name_plural = "discussions"


if not reversion.is_registered(Discussion):
    reversion.register(Discussion)
