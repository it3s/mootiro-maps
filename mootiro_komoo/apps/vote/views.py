# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.contrib.contenttypes.models import ContentType

from annoying.decorators import ajax_request, render_to

from vote.models import Vote

logger = logging.getLogger(__name__)


@render_to('vote/vote_poc.html')
def vote_poc(request):
    logger.debug('acessing vote > vote_poc')
    from need.models import Need
    need = Need.objects.get(pk=1)
    ct = ContentType.objects.get_for_model(need)
    votes = Vote.get_votes_for(need)
    votes_up = votes.filter(like=True).count()
    votes_down = votes.filter(like=False).count()
    return dict(content_object=need, content_type=ct.id, votes_up=votes_up,
                votes_down=votes_down)


def _get_from_request(request, field, method="POST"):
    return getattr(request, method)[field][0]


@ajax_request
def vote(request):
    logger.debug('acessing vote > vote : request:\n{}'.format(request.POST))
    if request.user and not request.user.is_anonymous():
        vote = request.POST['vote'] if 'vote' in request.POST else None
        content_type = request.POST['content_type'] \
            if 'content_type' in request.POST else None
        object_id = request.POST['object_id'] if 'object_id' in request.POST \
            else None

        content_object = ContentType.objects.get_for_id(content_type
                ).model_class().objects.get(pk=object_id)
        if not Vote.get_votes_for(content_object).filter(author=request.user).count():
            vote = Vote(content_object=content_object, author=request.user,
                 like=(True if vote == 'up' else False)).save()
            return {'success': True}
        else:
            return {'success': False, 'error': 'Usuario já votou!'}
    return {'success': False, 'error': 'Usuario não logado ou anônimo'}
