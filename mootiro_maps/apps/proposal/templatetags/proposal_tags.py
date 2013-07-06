# -*- coding:utf-8 -*-
from django import template

register = template.Library()


@register.inclusion_tag('proposal/proposal_summary_templatetag.html')
def proposal_summary(proposal):
    return dict(proposal=proposal)
