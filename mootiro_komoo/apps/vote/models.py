# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


class Vote(models.Model):
    """
    Vote Model. Should dinamically reference any table/object.
    """
    author = models.ForeignKey(User, blank=True, null=True)

    ## TODO need modeling

    # dynamic ref
    content_type = models.ForeignKey(ContentType,  null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    @classmethod
    def get_votes_for(klass, obj):
        obj_content_type = ContentType.objects.get_for_model(obj)
        return Vote.objects.filter(content_type=obj_content_type, object_id=obj.id)
