# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

# from django.contrib.contenttypes.models import ContentType

from annoying.decorators import ajax_request, render_to

from vote.models import Vote

logger = logging.getLogger(__name__)


@render_to('vote/vote_poc.html')
def vote_poc(request):
    logger.debug('acessing vote > vote_poc')
    from need.models import Need
    need = Need.objects.get(pk=1)
    return dict(content_object=need)


@ajax_request
def vote(request):
    logger.debug('acessing vote > vote : request:\n{}'.format(request.POST))
    if request.user and not request.user.is_anonymous():
        vote = request.POST['vote'] if 'vote' in request.POST else None
        content_type = request.POST['content_type'] \
            if 'content_type' in request.POST else None
        object_id = request.POST['object_id'] if 'object_id' in request.POST \
            else None
        vote_obj, created = Vote.objects.get_or_create(content_type=content_type,
                                object_id=object_id, author=request.user)
        print 'vote: {}  created: {}'.format(vote_obj, created)
        vote_obj.like = True if vote == 'up' else False
        vote_obj.save()
        print 'vote: {}   like: {}'.format(vote_obj, vote_obj.like)
        return {'success': True, 'created': created}
    return {'success': False, 'error': 'Usuario não logado ou anônimo'}
