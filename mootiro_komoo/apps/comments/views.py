# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from comments.forms import FormComment
from comments.models import Comment
from annoying.decorators import render_to, ajax_request

@render_to('comments/comments_poc.html')
def comments_index(request):
    form_comment = FormComment()
    comments = Comment.objects.filter(parent__isnull=True)
    
    return {'form_comment' : FormComment(), 'comments' : comments}

@ajax_request
def comments_add(request):
    form_comment = FormComment(request.POST)    
    if form_comment.is_valid():
        comment = form_comment.save() 
        return {
            'success' : True, 
            'comment': {
                'comment': comment.comment, 
                'id' : comment.id, 
                'pub_date' : comment.pub_date.strftime('%d/%m/%Y'),
                'sub_comments' : comment.sub_comments
            }
        } 
    else:
        return {'success' : False, 'errors' : form.errors} 
          
@ajax_request
def subcomments_load(request):
    return {}