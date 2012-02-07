#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.db import models


class Proposal(models.Model):
    '''http://dev.mootiro.org/projects/needs/wiki/EntidadesProposta'''
    name = models.CharField(max_length=256)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    content = models.TextField()  # TODO: tinymce
    # TODO: Proposal must belong to a Need
    # TODO: Realizadores (um ou mais relacionamentos p/ organizações ou pessoas)
    cost = models.DecimalField(decimal_places=2, max_digits=14)
    report = models.TextField()  # TODO: tinymce
    # TODO: creator. Proposal belongs to a user
    class Meta:
        app_label = 'komoo'  # needed for Django to find the model
        verbose_name = "solution proposal"
        verbose_name_plural = "solution proposals"
