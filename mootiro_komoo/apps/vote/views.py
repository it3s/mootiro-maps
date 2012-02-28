# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from annoying.decorators import ajax_request


@ajax_request
def vote(request):
    if not request.user and not request.user.is_anonymous():
        # receive data and save Vote
        pass
    return {}
