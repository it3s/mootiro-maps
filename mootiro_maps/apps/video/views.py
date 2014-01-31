#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import logging
from urlparse import urlparse, parse_qs
import requests
import json

import gdata.youtube.service

from django.http import HttpResponse
from django.conf import settings

from main.utils import to_json
from .models import Video

logger = logging.getLogger(__name__)

def get_video_info_from_url(url):
    if 'vimeo.com' in url:
        video_id = get_vimeo_video_id_from_url(url)
        service = Video.VIMEO
    elif 'youtu' in url:
        video_id = get_youtube_video_id_from_url(url)
        service = Video.YOUTUBE
    return get_video_info(service, video_id)


def get_youtube_video_id_from_url(url):
    """
    Examples:
    - http://youtu.be/<VIDEO_ID>
    - http://www.youtube.com/watch?v=<VIDEO_ID>&feature=feedu
    - http://www.youtube.com/embed/<VIDEO_ID>
    - http://www.youtube.com/v/<VIDEO_ID>?version=3&amp;hl=en_US
    """
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None

def get_vimeo_video_id_from_url(url):
    """
    Examples:
    - http://vimeo.com/<VIDEO_ID>
    - http://player.vimeo.com/video/<VIDEO_ID>
    """
    query = urlparse(url)
    if query.hostname in ('www.vimeo.com', 'vimeo.com'):
        return query.path[1:]
    print query.hostname
    if query.hostname == 'player.vimeo.com':
        if query.path[:7] == '/video/':
            return query.path.split('/')[2]
    # fail?
    return None

def get_video_info(service, video_id):
    services = {
        Video.YOUTUBE: get_youtube_video_info,
        Video.VIMEO: get_vimeo_video_info,
    }
    return services.get(service, lambda x: {})(video_id)


yt_service = gdata.youtube.service.YouTubeService()
yt_service.ssl = False
yt_service.developer_key = settings.GOOGLE_API_KEY

def get_youtube_video_info(video_id):
    try:
        video = yt_service.GetYouTubeVideoEntry(video_id=video_id)
        info = {
            'status': 200,
            'service': Video.YOUTUBE,
            'title': video.media.title.text,
            'description': video.media.description.text,
            'video_id': video_id,
            'video_url': video.media.player.url,
            'thumbnail_url': video.media.thumbnail[0].url,
        }
    except Exception as e:
        # {'status': ..., 'body':..., 'reason':...}
        info = e.message
    return info

def get_vimeo_video_info(video_id):
    try:
        r = requests.get("http://vimeo.com/api/v2/video/{}.json".format(video_id))
        video = json.loads(r.text)[0]
        info = {
            'status': 200,
            'service': Video.VIMEO,
            'title': video.get('title', ''),
            'description': video.get('description', '').replace('<br />', ''),
            'video_id': video_id,
            'video_url': video.get('url', ''),
            'thumbnail_url': video.get('thumbnail_medium', ''),
        }
    except Exception as e:
        info = None
    return info

def youtube_info(request, video_id=None):
    info = get_youtube_video_info(video_id)
    return HttpResponse(to_json(info),
                        mimetype="application/x-javascript")

def url_info(request):
    url = request.POST.get('video_url', None)
    if url:
        success = True
        video_ = get_video_info_from_url(url)
    else:
        success = False
        video_ = {}
    return HttpResponse(to_json({'success': success, 'video': video_}),
                        mimetype="application/x-javascript")

