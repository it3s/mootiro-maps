# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse


def index(request, community_slug=''):
    return HttpResponse('HEllo organizations<br/>%s' % community_slug)
