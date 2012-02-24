# -*- coding:utf-8 -*-
from django import template
from django.contrib.contenttypes.models import ContentType
from ..forms import FormComment
from ..views import comments_list

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
    Templatetags for comments. It returns a rendered template for the comments of a given content_object
    params:
        content_object : object to get/link the comments
        arg1/arg2 : arguments for width/heigth. You must pass a string like: 'width=5', 'height=12'

    examples:
        {% comments need %}
        {% comments proposal 'width=7' %}
        {% comments proposal 'height=6' 'width=3' %}
    """
    parsed_args = _parse_args(arg1, arg2)
    width, height = parsed_args.get('width', 0), parsed_args.get('height', 5)

    c = ContentType.objects.get_for_model(content_object)
    form = FormComment(initial={'content_type_id': c.id, 'object_id': content_object.id})

    comments = comments_list(content_object=content_object, width=width, height=height, root=True).content
    return {'form_comment': form, 'comments_list': comments}


@register.inclusion_tag('comments/comments_staticfiles.html')
def comments_staticfiles():
    """Static files (javascript/css) for the comments templatetag"""
    return {}
