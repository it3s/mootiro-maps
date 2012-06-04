#coding: utf-8
from django import template
from django.contrib.contenttypes.models import ContentType
from moderation.models import Moderation, Report
from moderation.utils import get_reports_by_user

register = template.Library()


@register.inclusion_tag('moderation/report_content_button_templatetag.html',
        takes_context=True)
def report_content(context, obj):
    """
    The syntax:
        {% report_content object %}
    """
    content_type = ContentType.objects.get_for_model(obj)
    user = context.get('user', None)
    reports = get_reports_by_user(user, obj)
    return dict(app_label=content_type.app_label,
                model_name=content_type.name,
                id=obj.id,
                reports=reports)


@register.inclusion_tag('moderation/delete_button_templatetag.html',
        takes_context=True)
def delete_button(context, obj):
    """
    The syntax:
        {% delete_button object %}
    """
    content_type = ContentType.objects.get_for_model(obj)
    return dict(app_label=content_type.app_label,
                model_name=content_type.name,
                id=obj.id)


@register.inclusion_tag('moderation/report_content_box_templatetag.html',
        takes_context=True)
def report_content_box(context):
    """
    The syntax:
        {% report_content_box %}
    """

    return dict(types=Report.REASON_NAMES.items()[1:])
