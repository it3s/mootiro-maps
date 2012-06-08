#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls.defaults import *


urlpatterns = patterns('signatures.views',
    url(r'follow$', 'follow', name='follow_content'),
)
