# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from video.models import Video

register = template.Library()


@register.inclusion_tag('video/edit_tag.html', takes_context=True)
def load_videos(context, obj=None):
    if obj:
        videos = Video.get_videos_for(obj)
        object_id = obj.id
        content_type = ContentType.objects.get_for_model(obj).id
    else:
        videos = []
        object_id = ''
        content_type = ''
    return dict(videos=videos, object_id=object_id, content_type=content_type)


@register.inclusion_tag('video/video_gallery.html', takes_context=True)
def video_gallery(context, obj=None):
    videos = Video.get_videos_for(obj) if obj else []
    return dict(videos=videos, STATIC_URL=settings.STATIC_URL)
