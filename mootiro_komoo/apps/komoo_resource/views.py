# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from annoying.decorators import ajax_request


@ajax_request
def index(request):
    # dummy
    return {}
