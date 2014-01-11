#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from jsonfield import JSONField

from authentication.models import User


class ModelVersion(models.Model):
    table_ref = models.CharField(max_length=256)
    object_id = models.IntegerField()
    creator = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now_add=True)
    data = JSONField()

    def __unicode__(self):
        return "ModelVersion:[%s :: %s]" % (self.table_ref, self.object_id)

