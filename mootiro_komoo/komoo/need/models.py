#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.db import models

from komoo.community.models import Community


class Need(models.Model):
    CATEGORY_CHOICES = (
        ('ENV', 'Environment'),
        ('HLT', 'Health'),
        ('EDU', 'Education'),
    )
    AUDIENCE_CHOICES = (
        ('CHL', '0-12'),
        ('TEN', '12-18'),
        ('MIN', 'Minorities'),
    )

    title = models.CharField(max_length=256)
    description = models.TextField()
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES)
    target_audience = models.CharField(max_length=3, choices=AUDIENCE_CHOICES)

    community = models.ForeignKey(Community, related_name="needs")

    class Meta:
        app_label = 'komoo'  # needed for Django to find the model
