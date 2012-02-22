# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.shortcuts import render_to_response
from django.template import RequestContext

from annoying.decorators import render_to, ajax_request

from komoo_comments.forms import FormComment
from komoo_comments.models import Comment

logger = logging.getLogger(__name__)


@render_to('comments/comments_poc.html')
def comments_index(request):
    logger.debug('accessing Comments > comments_index')

    return {'form_comment': FormComment(), 'comments_list': comments_list(context=RequestContext(request), **request.GET).content}


@ajax_request
def comments_add(request):
    logger.debug('accessing Comments > comments_add')

    form_comment = FormComment(request.POST)
    if form_comment.is_valid():
        comment = form_comment.save()
        return {
            'success': True,
            'comment': render_to_response('comments/comment.html', dict(comment=comment), context_instance=RequestContext(request)).content
        }
    else:
        logger.debug('invalid form: {}'.format(form_comment.errors))
        return {'success': False, 'errors': form_comment.errors}


def comments_list(parent_id=None, width=1, height=10, context=None, inner=False):
    logger.debug('accessing Comments > comments_list')
    width = int(width[0]) if isinstance(width, list) else int(width)
    height = int(height[0]) if isinstance(height, list) else int(height)
    parent_id = int(parent_id[0]) if parent_id and isinstance(parent_id, list) else parent_id

    logger.debug('loading comment with parent={} , width={} , height={}'.format(parent_id, width, height))
    if parent_id:
        comments = Comment.objects.filter(parent=parent_id).order_by('-pub_date')[:height]
    else:
        comments = Comment.objects.filter(parent__isnull=True).order_by('-pub_date')[:height]
    if width:
        for comment in comments:
            if comment.sub_comments > 0:
                comment.sub_comments_list = comments_list(parent_id=comment.id, width=width - 1, context=context).content
    return render_to_response('comments/comments_list.html', dict(parent_id=parent_id, comments=comments, inner=inner), context_instance=context)


@ajax_request
def comments_load(request):
    return dict(comments=comments_list(context=RequestContext(request), inner=True, **request.GET).content)
