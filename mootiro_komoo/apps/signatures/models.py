# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class Signature(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType,  null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    digest = models.BooleanField(default=False)  # deprecated

    class Meta:
        unique_together = (("user", "content_type", "object_id"),)


class WeeklySignature(models.Model):
    user = models.ForeignKey(User)
    last_send = models.DateTimeField(auto_now_add=True)


class WeeklyDigest(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType,  null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    inclusion_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "content_type", "object_id"),)
