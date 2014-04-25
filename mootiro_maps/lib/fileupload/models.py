# -*- coding: utf-8 -*-
import os
import time
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


def file_upload(instance, filename):
    ext = filename[filename.rindex('.'):] if filename.rindex('.') else ''
    return os.path.join('upload', '{fname}{ext}'.format(
                            fname=int(time.time() * 1000), ext=ext))


class UploadedFile(models.Model):

    file = models.FileField(upload_to=file_upload)
    subtitle = models.TextField(null=True, blank=True)
    cover = models.NullBooleanField(null=True, blank=True)

    # dynamic ref
    content_type = models.ForeignKey(ContentType,  null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return unicode(self.file.name).encode('utf-8')

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )

    @classmethod
    def get_files_for(klass, obj):
        obj_content_type = ContentType.objects.get_for_model(obj)
        return UploadedFile.objects.filter(content_type=obj_content_type,
                                           object_id=obj.id)

    @classmethod
    def bind_files(cls, ids_list, obj_to_bind):
        """
        class method to bind a list of files to a given obj
        """
        for f in ids_list:
            if f:
                file_ = UploadedFile.objects.get(pk=f)
                file_.content_object = obj_to_bind
                file_.save()

