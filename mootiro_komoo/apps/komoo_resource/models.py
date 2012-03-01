# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class Resource(models.Model):
    """Resources model"""
    author = models.ForeignKey(User, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    # tipo = models.ForeignKey(?)
    description = models.TextField()
    # images = ?
    # other media ? video?
