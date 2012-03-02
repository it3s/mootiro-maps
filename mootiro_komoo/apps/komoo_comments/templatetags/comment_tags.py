# -*- coding:utf-8 -*-
from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from ..forms import FormComment
from ..views import comments_list
from ..models import Comment

register = template.Library()


def _parse_args(*args):
    parsed_args = {}
    for arg in args:
        if arg:
            a = arg.split('=')
            parsed_args[a[0]] = a[1]
    return parsed_args


@register.inclusion_tag('comments/comments_templatetag.html', takes_context=True)
def comments(context, content_object, arg1='', arg2=''):
    """
    Templatetags for comments. It returns a rendered template for the comments
    of a given content_object
    params:
        content_object : object to get/link the comments
        arg1/arg2 : arguments for width/heigth. You must pass a string like: '
            width=5', 'height=12'

    examples:
        {% comments need %}
        {% comments proposal 'width=7' %}
        {% comments proposal 'height=6' 'width=3' %}
    """
    parsed_args = _parse_args(arg1, arg2)
    width = parsed_args.get('width', settings.KOMOO_COMMENTS_WIDTH)
    height = parsed_args.get('height', settings.KOMOO_COMMENTS_HEIGHT)

    c = ContentType.objects.get_for_model(content_object)
    form = FormComment(initial={'content_type_id': c.id,
                                'object_id': content_object.id})

    comments = comments_list(content_object=content_object, context=context,
                    width=width, height=height, root=True).content
    has_comments = Comment.get_comments_for(content_object).count()
    return dict(form_comment=form, comments_list=comments, width=width,
                height=height, content_type=c.id, object_id=content_object.id,
                has_comments=has_comments)


@register.inclusion_tag('comments/comments_summary_templatetag.html', takes_context=True)
def comments_summary(context, content_object):
    """Templatetags for embedded comments summary."""
    num_comments = Comment.get_comments_for(content_object).count()
    return dict(num_comments=num_comments)



@register.inclusion_tag('comments/comments_staticfiles.html')
def comments_staticfiles():
    """Static files (javascript/css) for the comments templatetag"""
    return {}
