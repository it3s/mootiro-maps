# -*- coding:utf-8 -*-
from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('update/updates_list_templatetag.html')
def updates_list(updates_page, compact=False):
    '''Templatetag for showing an updates list.'''
    return dict(updates_page=updates_page, STATIC_URL=settings.STATIC_URL,
                compact=bool(compact))
