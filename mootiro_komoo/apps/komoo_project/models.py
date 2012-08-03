# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
# from django.contrib.contenttypes.models import ContentType

from lib.taggit.managers import TaggableManager
from fileupload.models import UploadedFile


class Project(models.Model):
    name = models.CharField(max_length=1024)
    slug = models.SlugField(max_length=1024)
    description = models.TextField()
    tags = TaggableManager()

    logo = models.ForeignKey(UploadedFile, null=True, blank=True)
    creator = models.ForeignKey(User, editable=False, null=True,
            related_name='created_projects')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_editor = models.ForeignKey(User, editable=False, null=True,
            blank=True)
    last_update = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return unicode(self.name)

# TODO urls + reversion

# class ProjectRelationship(models.Model):
#     project = models.ForeignKey(Project)
#     content_object ?
