# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from annoying.decorators import render_to, ajax_request

from komoo_comments.forms import FormComment
from komoo_comments.models import Comment

logger = logging.getLogger(__name__)

@render_to('comments/comments_poc.html')
def comments_index(request):
    logger.debug('accessing Comments > comments_index')
    form_comment = FormComment()
    comments = Comment.objects.filter(parent__isnull=True).order_by('-pub_date')

    return {'form_comment' : FormComment(), 'comments' : comments}

@ajax_request
def comments_add(request):
    logger.debug('accessing Comments > comments_add')

    form_comment = FormComment(request.POST)
    if form_comment.is_valid():
        comment = form_comment.save()
        #return HttpResponseRedirect(reverse('comments_index'))
        return {
            'success' : True,
            'comment': {
                'id' : comment.id,
                'comment' : comment.comment,
                'pub_date' : comment.pub_date.strftime('%d/%m/%Y, %H:%M'),
                'author' : 'User goes here!',
                'sub_comments' : comment.sub_comments
            }
        }
    else:
        logger.debug('invalid form: {}'.format(form_comment.errors))
        return {'success' : False, 'errors' : form_comment.errors}

@ajax_request
def comments_load(request):
    logger.debug('accessing Comments > comments_load')
    id_ = request.GET.get('id', None)
    logger.debug('loading comment with parent "{}"'.format(id_))
    if id_:
        comments = Comment.objects.filter(parent = id_).order_by('-pub_date')
        return {'success' : True, 'comments' : [
                    {'id' : c.id, 'comment' : c.comment, 'pub_date' : c.pub_date.strftime('%d/%m/%Y, %H:%M'),
                     'author' : 'Author goes here!', 'sub_comments' : c.sub_comments} for c in comments]}
    else:
        logger.debug('parent id not given')
        return {'success' : False }