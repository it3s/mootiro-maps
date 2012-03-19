# -*- coding:utf-8 -*-
from django import template
from community.models import Community
from need.models import Need
from proposal.models import Proposal

register = template.Library()


def _get_related_community(obj):
    if isinstance(obj, Community):
        community = obj
    elif isinstance(obj, Need):
        community = obj.community
    elif isinstance(obj, Proposal):
        community = obj.need.community
    else:
        community = None
    return community


@register.inclusion_tag('main/menu_templatetag.html')
def menu(obj=None, selected_area=''):
    community = _get_related_community(obj)
    return dict(community=community, selected_area=selected_area)


@register.inclusion_tag('main/community_tabs_templatetag.html')
def community_tabs(obj=None):
    community = _get_related_community(obj)
    return dict(community=community)


@register.inclusion_tag('main/track_buttons_templatetag.html')
def track_buttons():
    return dict()


@register.inclusion_tag('main/taglist_templatetag.html')
def taglist(obj):
    return dict(object=obj)


@register.inclusion_tag('main/pagination_templatetag.html')
def pagination(collection):
    return dict(collection=collection)
