# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from authentication.models import User


DIGEST_CHOICES = (
        ('D', 'Daily'),
        ('W', 'Weekly'),
    )


class SignedContent(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType,  null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True


class Signature(SignedContent):
    digest = models.BooleanField(default=False)  # deprecated

    class Meta:
        unique_together = (("user", "content_type", "object_id"),)


class DigestSignature(models.Model):
    user = models.ForeignKey(User)
    last_send = models.DateTimeField(auto_now_add=True)  # necessary?
    digest_type = models.CharField(max_length=1, choices=DIGEST_CHOICES, default='D')


class Digest(SignedContent):
    inclusion_date = models.DateTimeField(auto_now_add=True)
    digest_type = models.CharField(max_length=1, choices=DIGEST_CHOICES, default='D')

    class Meta:
        unique_together = (("user", "content_type", "object_id"),)

