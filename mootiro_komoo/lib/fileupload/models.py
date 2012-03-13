# -*- coding: utf-8 -*-
import os
import time
from django.db import models
# from django.template.defaultfilters import slugify


def file_upload(instance, filename):
    ext = filename[filename.rindex('.'):]
    return os.path.join('upload', '{fname}{ext}'.format(
                            fname=int(time.time() * 1000), ext=ext))


class UploadedFile(models.Model):

    file = models.FileField(upload_to=file_upload)
    # slug = models.SlugField(max_length=50, blank=True)

    # TODO: reference from any object
    # content_type = models.ForeignKey(ContentType)
    # object_id = models.IntegerField()
    # content_object = models.?

    def __unicode__(self):
        return self.file

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )

    # def save(self, *args, **kwargs):
    #     # self.slug = slugify(self.file.name)
    #     super(UploadedFile, self).save(*args, **kwargs)
