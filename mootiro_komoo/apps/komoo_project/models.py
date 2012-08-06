# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
# from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from lib.taggit.managers import TaggableManager
from fileupload.models import UploadedFile

from main.utils import slugify


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

    def slug_exists(self, slug):
        return Project.objects.filter(slug=slug).exists()

    def save(self, *a, **kw):
        old_title = Project.objects.get(id=self.id).name if self.id else None
        if not self.id or old_title != self.name:
            self.slug = slugify(self.name,
                    lambda slug: Project.objects.filter(slug=slug).exists())
        return super(Project, self).save(*a, **kw)

    @property
    def home_url_params(self):
        return dict(project_slug=self.slug)

    @property
    def view_url(self):
        return reverse('project_view', kwargs=self.home_url_params)

    @property
    def edit_url(self):
        return reverse('project_edit', kwargs=self.home_url_params)

    # @property
    # def admin_url(self):
    #     return reverse('admin:{}_{}_change'.format(self._meta.app_label,
    #         self._meta.module_name), args=[self.id])


# TODO urls + reversion

# class ProjectRelationship(models.Model):
#     project = models.ForeignKey(Project)
#     content_object ?
