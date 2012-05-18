# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.utils.translation import ugettext_lazy as _
from django.db.models import F
from django.contrib.contenttypes.models import ContentType

from annoying.decorators import ajax_request, render_to

from vote.models import Vote

logger = logging.getLogger(__name__)


@render_to('vote/vote_poc.html')
def vote_poc(request):
    """Proof of concept (test) for voting"""
    logger.debug('acessing vote > vote_poc')
    from need.models import Need
    need = Need.objects.get(pk=1)
    return dict(content_object=need)


@ajax_request
def vote(request):
    """
    method for voting.
    It ensures the user is authenticated then creates or update a
    vote given a content_type and  a object_id.
    params:
        vote: String 'up' or 'down' for your vote
        object_id: id of the object you are voting
        content_type: id of the content_type you are voting
    """
    logger.debug('acessing vote > vote : request:\n{}'.format(request.POST))
    if request.user and not request.user.is_anonymous():
        vote = request.POST['vote'] if 'vote' in request.POST else None
        content_type = request.POST['content_type'] \
            if 'content_type' in request.POST else None
        object_id = request.POST['object_id'] if 'object_id' in request.POST \
            else None
        vote_obj, created = Vote.objects.get_or_create(content_type_id=content_type,
                                object_id=object_id, author=request.user)
        vote_obj.like = True if vote == 'up' else False
        vote_obj.save()

        # now denormalize everything
        obj = ContentType.objects.get(pk=content_type
                    ).model_class().objects.get(pk=object_id)
        if not created:
            old_vote = {'up': 'down', 'down': 'up'}
            if getattr(obj, 'votes_' + old_vote[vote]) > 0:
                setattr(obj, 'votes_' + old_vote[vote],
                            F('votes_' + old_vote[vote]) - 1)
        setattr(obj, 'votes_' + vote, F('votes_' + vote) + 1)
        obj.save()
        return {'success': True, 'created': created}
    return {'success': False, 'error': _('User not logged or anonymous')}
