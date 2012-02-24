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
    from need.models import Need
    return {'content_object': Need.objects.get(pk=1)}
    # return {'content_object': None}


@ajax_request
def comments_add(request):
    logger.debug('accessing Comments > comments_add : POST={}'.format(request.POST))

    form_comment = FormComment(request.POST)
    if form_comment.is_valid():
        comment = form_comment.save()
        return {
            'success': True,
            'comment': render_to_response('comments/comment.html', dict(comment=comment, comment_class=''), context_instance=RequestContext(request)).content
        }
    else:
        logger.debug('invalid form: {}'.format(form_comment.errors))
        return {'success': False, 'errors': form_comment.errors}


def comments_list(content_object=None, parent_id=None, page=0, width=0, height=10, context=None, comment_class='', wrap=True, root=False):
    """
    builds a list o comments recursivelly and returns its rendered template
    params:
        parent_id : id of the parent for subcomments (default: None -> retrieves root comments)
        page : page number
        width: depth of subcomments to be loaded
        height: number of 'root' (in this sub-tree) comments to be loaded
        context: a RequestContext object, needed for csrf purposes
        comment_class: used for controlling the css classes (depth striped) on comment-container
        root : flag to identify if its a root comment
    """
    logger.debug('accessing Comments > comments_list')
    width = int(width[0]) if isinstance(width, list) else int(width)
    height = int(height[0]) if isinstance(height, list) else int(height)
    parent_id = int(parent_id[0]) if parent_id and isinstance(parent_id, list) else parent_id
    wrap = int(wrap[0]) if wrap and isinstance(wrap, list) else wrap
    page = int(page[0]) if isinstance(page, list) else int(page)

    logger.debug('loading comment with parent={} , page={} , width={} , height={}'.format(parent_id, page, width, height))
    start, end = page * height, (page + 1) * height
    comments_query = Comment.get_comments_for(content_object) if content_object else Comment.objects
    if parent_id:
        comments = comments_query.filter(parent=parent_id).order_by('-pub_date')[start:end]
    else:
        comments = comments_query.filter(parent__isnull=True).order_by('-pub_date')[start:end]
    if width:
        for comment in comments:
            if comment.sub_comments > 0:
                comment.sub_comments_list = comments_list(parent_id=comment.id, width=width - 1,
                    comment_class='inner-comment' if 'odd' in comment_class else 'inner-comment odd',
                    context=context).content
    if not root:
        comment_class += ' inner-comment'
    return render_to_response('comments/comments_list.html',
            dict(parent_id=parent_id, comments=comments, comment_class=comment_class, wrap=wrap),
            context_instance=context)


@ajax_request
def comments_load(request):
    return dict(comments=comments_list(context=RequestContext(request), **request.GET).content)
