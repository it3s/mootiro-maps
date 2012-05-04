#coding: utf-8
from django import template
register = template.Library()


@register.inclusion_tag('investment/investment_list_templatetag.html')
def investments_list(received_investments, realized_investments=None):
    return dict(received=received_investments, realized=realized_investments,
                both=False if realized_investments == None else True)
