# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('video.views',
    url(r'^youtube/(?P<video_id>[\w.@+-]+)/info/?$', 'youtube_info', name='video_youtube_info'),
    url(r'^info_from_url/?$', 'url_info', name='video_url_info'),
)
