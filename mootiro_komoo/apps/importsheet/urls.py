# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import url, patterns
from mootiro_komoo.urls import prepare_regex as pr


urlpatterns = patterns('importsheet.views',
    url(pr(r'^poc/?$'), 'poc', name='importsheet'),
)
