# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.contenttypes.models import ContentType
from annoying.decorators import ajax_request, render_to


@render_to('vote/vote_poc.html')
def vote_poc(request):
    from need.models import Need
    need = Need.objects.get(pk=1)
    ct = ContentType.objects.get_for_model(need)
    return dict(content_object=need, content_type=ct.id)


@ajax_request
def vote(request):
    if not request.user and not request.user.is_anonymous():
        # receive data and save Vote
        pass
    return {}
