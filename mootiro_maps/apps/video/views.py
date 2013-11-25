#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import logging
from urlparse import urlparse, parse_qs


import gdata.youtube.service

from django.http import HttpResponse
from django.conf import settings

from main.utils import to_json

logger = logging.getLogger(__name__)

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

def get_video_info(provider, video_id):
    providers = {
        'youtube': get_youtube_video_info,
    }
    return providers.get(provider, lambda x: {})(video_id)

def get_youtube_video_info(video_id):
    yt_service = gdata.youtube.service.YouTubeService()
    yt_service.ssl = False
    yt_service.developer_key = settings.GOOGLE_API_KEY

    try:
        video = yt_service.GetYouTubeVideoEntry(video_id=video_id)
        info = {
            'status': 200,
            'video_id': video_id,
            'provider': 'youtube',
            'title': video.media.title.text,
            'author': video.author[0].name.text,
            'duration': video.media.duration.seconds,
            'published': video.published.text,
            'description': video.media.description.text,
            'thumbnail': video.media.thumbnail[0].url,
            'url': video.media.player.url,
        }
    except Exception as e:
        # {'status': ..., 'body':..., 'reason':...}
        info = e.message
    return info

def youtube_info(request, video_id=None):
    info = get_youtube_video_info(video_id)
    return HttpResponse(to_json(info),
                        mimetype="application/x-javascript")

def url_info(request):
    url = request.POST.get('video_url', None)
    provider = 'youtube'
    video_id = get_youtube_video_id_from_url(url)
    if video_id:
        success = True
        video_ = get_video_info(provider, video_id)
    else:
        success = False
        video_ = {}
    return HttpResponse(to_json({'success': success, 'video': video_}),
                        mimetype="application/x-javascript")

