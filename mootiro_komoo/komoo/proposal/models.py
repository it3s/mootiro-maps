#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.db import models
from django.contrib.auth.models import User
# from ..need.models import Need


class Proposal(models.Model):
    '''http://dev.mootiro.org/projects/needs/wiki/EntidadesProposta'''
    name = models.CharField('proposal name', max_length=256)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    content = models.TextField()

    # Relationships
    need = models.ForeignKey('Need', related_name='proposals')
    creator = models.ForeignKey(User, related_name='proposals_created')

    # Consummation, realization, attainment:
    realizers = models.ManyToManyField(User)
    # TODO: Also: organizations = model.ManyToManyField(Organization)
    cost = models.DecimalField(decimal_places=2, max_digits=14, null=True)
    report = models.TextField()

    class Meta:
        app_label = 'komoo'  # needed for Django to find the model
        verbose_name = "solution proposal"
        verbose_name_plural = "solution proposals"
