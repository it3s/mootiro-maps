# -*- coding:utf-8 -*-
from django import template
from ..forms import FormComment

register = template.Library()


@register.inclusion_tag('comments/comments_templatetag.html')
def comments(comments):
    return {'form_comment': FormComment(), 'comments_list': comments}


@register.inclusion_tag('comments/comments_staticfiles.html')
def comments_staticfiles():
    return {}
