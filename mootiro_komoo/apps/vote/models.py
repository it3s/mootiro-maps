# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


class Vote(models.Model):
    """
    Vote Model. Should dinamically make reference to any table/object.
    """
    author = models.ForeignKey(User, blank=True, null=True)

    like = models.BooleanField()

    # dynamic ref
    content_type = models.ForeignKey(ContentType,  null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    @classmethod
    def get_votes_for(klass, obj):
        """
        returns a queryset for the votes of for any given object.
        It can be chained later with any filter
        """
        obj_content_type = ContentType.objects.get_for_model(obj)
        return Vote.objects.filter(content_type=obj_content_type,
            object_id=obj.id)
