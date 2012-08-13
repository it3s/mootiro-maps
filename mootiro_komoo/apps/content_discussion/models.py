# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

import reversion


class ContentDiscussion(models.Model):
    text = models.TextField(null=True, blank=True)

    last_editor = models.ForeignKey(User, editable=False, null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)

    # Generic Relationship
    content_type = models.ForeignKey(ContentType, editable=False, null=True)
    object_id = models.PositiveIntegerField(editable=False, null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')


if not reversion.is_registered(ContentDiscussion):
    reversion.register(ContentDiscussion)
