#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.db import models


class Proposal(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    # TODO: Proposal must belong to a Need
    class Meta:
        app_label = 'komoo'  # needed for Django to find the model
        verbose_name = "solution proposal"
        verbose_name_plural = "solution proposals"
