# -*- coding:utf-8 -*-
from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('highlight/highlight_section_templatetag.html')
def highlight_section(highlight_section):
    """Templatetag for displaying a given highlight section."""
    return dict(hs=highlight_section)
