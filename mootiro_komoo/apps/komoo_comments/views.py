# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from komoo_comments.forms import FormComment
from komoo_comments.models import Comment
from annoying.decorators import render_to, ajax_request

@render_to('comments/comments_poc.html')
def comments_index(request):
    form_comment = FormComment()
    comments = Comment.objects.filter(parent__isnull=True).order_by('-pub_date')

    return {'form_comment' : FormComment(), 'comments' : comments}

@ajax_request
def comments_add(request):
    form_comment = FormComment(request.POST)
    if form_comment.is_valid():
        comment = form_comment.save()
        return HttpResponseRedirect(reverse('comments_index'))
        # return {
        #     'success' : True,
        #     'comment': {
        #         'comment': comment.comment,
        #         'id' : comment.id,
        #         'pub_date' : comment.pub_date.strftime('%d/%m/%Y'),
        #         'sub_comments' : comment.sub_comments
        #     }
        # }
    else:
        return {'success' : False, 'errors' : form_comment.errors}

@ajax_request
def comments_load(request):
    id_ = request.GET.get('id', None)
    print 'is is %s' % id_
    if id_:
        comments = Comment.objects.filter(parent = id_).order_by('-pub_date')
        return {'success' : True, 'comments' : [
                    {'id' : c.id, 'content' : c.comment, 'pub_date' : c.pub_date.strftime('%d/%m/%Y, %H:%M'),
                     'author' : 'Author goes here!', 'sub_comments' : c.sub_comments} for c in comments]}
    else:
        return {'success' : False }