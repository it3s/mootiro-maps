# -*- coding:utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django import template
from django import forms

from main.utils import templatetag_args_parser
from main.widgets import ImageSwitch, ImageSwitchMultiple
from community.models import Community
from need.models import Need, NeedCategory
from organization.models import Organization
from komoo_resource.models import Resource
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


@register.inclusion_tag('main/geo_objects_listing_templatetag.html')
def geo_objects_listing(arg1='', arg2=''):
    """Usage: {% geo_objects_listing [show_categories] [switchable] %}"""
    parsed_args = templatetag_args_parser(arg1, arg2)
    show_categories = parsed_args.get('show_categories', False)
    switchable = parsed_args.get('switchable', False)

    img = {
        'communities': Community.image,
        'communities_off': Community.image_off if switchable else Community.image,
        'needs': Need.image,
        'needs_off': Need.image_off if switchable else Need.image,
        'organizations': Organization.image,
        'organizations_off': Organization.image_off if switchable else Organization.image,
        'resources': Resource.image,
        'resources_off': Resource.image_off if switchable else Resource.image,
    }

    image_field = lambda image, image_off: \
        forms.BooleanField(
            widget=ImageSwitch(image_tick=image, image_no_tick=image_off)
        )

    class GeoObjectsForm(forms.Form):
        communities = image_field(img['communities'], img['communities_off'])
        needs = image_field(img['needs'], img['needs_off'])
        organizations = image_field(img['organizations'], img['organizations_off'])
        resources = image_field(img['resources'], img['resources_off'])

        need_categories = forms.ModelMultipleChoiceField(
            queryset=NeedCategory.objects.all().order_by('name'),
            widget=ImageSwitchMultiple(
                get_image_tick=NeedCategory.get_image,
                get_image_no_tick=NeedCategory.get_image_off if switchable \
                                    else NeedCategory.get_image,
                show_names=True
            )
        )

    form = GeoObjectsForm()

    return dict(form=form, show_categories=show_categories)


@register.inclusion_tag('main/track_buttons_templatetag.html')
def track_buttons():
    return dict()


@register.inclusion_tag('main/taglist_templatetag.html')
def taglist(obj):
    return dict(object=obj)


@register.inclusion_tag('main/pagination_templatetag.html')
def pagination(collection):
    return dict(collection=collection)


@register.filter
def with_http(link):
    """prepends http:// to a given link if it does not already have"""
    return 'http://{link}'.format(link=link) if not 'http://' in link else link
