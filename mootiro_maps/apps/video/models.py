# -*- coding: utf-8 -*-
import os
import time
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class Video(models.Model):
#
#    file = models.FileField(upload_to=file_upload)
#    subtitle = models.TextField(null=True, blank=True)
#
#    # dynamic ref
#    content_type = models.ForeignKey(ContentType,  null=True, blank=True)
#    object_id = models.PositiveIntegerField(null=True, blank=True)
#    content_object = generic.GenericForeignKey('content_type', 'object_id')
#
#    def __unicode__(self):
#        return unicode(self.file.name).encode('utf-8')
#
#    @models.permalink
#    def get_absolute_url(self):
#        return ('upload-new', )
#
    @classmethod
    def get_videos_for(cls, obj):
        return []
#
#    @classmethod
#    def bind_files(cls, ids_list, obj_to_bind):
#        """
#        class method to bind a list of files to a given obj
#        """
#        for f in ids_list:
#            if f:
#                file_ = UploadedFile.objects.get(pk=f)
#                file_.content_object = obj_to_bind
#                file_.save()
#
