# -*- coding:utf-8 -*-
from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('discussion/discussion_tab_templatetag.html')
def discussion_tab(content_object, content_id):
    """Templatetag for discussion tab on any content."""
    return dict(content_object=content_object, content_id=content_id)
