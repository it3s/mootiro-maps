# -*- coding: utf-8 -*-
import os
import time
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from main.utils import build_obj_from_dict


class Video(models.Model):
    YOUTUBE = 'YT'
    VIMEO = 'VI'

    SERVICE_CHOICES = (
        (YOUTUBE, 'YouTube'),
        (VIMEO, 'Vimeo'),
    )

    title = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    video_url = models.URLField()
    video_id = models.CharField(max_length=100)
    thumbnail_url = models.URLField(null=True, blank=True)
    service = models.CharField(max_length=2, choices=SERVICE_CHOICES)

    # dynamic ref
    content_type = models.ForeignKey(ContentType,  null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return unicode(self.title).encode('utf-8')

    @classmethod
    def get_videos_for(cls, obj):
        obj_content_type = ContentType.objects.get_for_model(obj)
        return Video.objects.filter(content_type=obj_content_type,
                                    object_id=obj.id)

    @classmethod
    def save_videos(cls, videos_list, obj_to_bind):
        """
        class method to save and bind a list of videos to a given obj
        """
        for video_ in videos_list:
            if video_.get('id', '') != '':
                video = Video.objects.get(pk=video_['id'])
            else:
                video = Video()
            video_status = video_.get('status', '')
            if video_status == 'deleted':
                video.delete()
            else:
                video.from_dict(video_)
                video.content_object = obj_to_bind
                video.save()

    def from_dict(self, data):
        keys = [
            'title',
            'description',
            'video_url',
            'video_id',
            'thumbnail_url',
            'service',
        ]
        build_obj_from_dict(self, data, keys)

