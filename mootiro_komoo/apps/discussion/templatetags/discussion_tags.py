# -*- coding:utf-8 -*-
from django import template
from django.conf import settings

register = template.Library()


def _parse_args(*args):
    parsed_args = {}
    for arg in args:
        if arg:
            a = arg.split('=')
            parsed_args[a[0]] = a[1]
    return parsed_args


@register.inclusion_tag('discussion/discussion_tab_templatetag.html')
def discussion_tab(content_object):
    """Templatetag for discussion tab on any content."""
    return dict()
