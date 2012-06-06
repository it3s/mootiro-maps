#coding: utf-8
from django import template
from moderation.models import Report
from moderation.utils import can_delete, get_reports_by_user

register = template.Library()


@register.inclusion_tag('moderation/report_content_button_templatetag.html',
        takes_context=True)
def report_content(context, obj, button_type='button'):
    """The syntax: {% report_content object %}"""
    user = context.get('user', None)
    reports = get_reports_by_user(user, obj)
    disabled = reports.count() > 0
    return dict(app_label=obj._meta.app_label,
                model_name=obj._meta.module_name,
                id=obj.id,
                disabled=disabled,
                button_type=button_type)


@register.inclusion_tag('moderation/delete_button_templatetag.html',
        takes_context=True)
def delete_button(context, obj):
    """The syntax: {% delete_button object %}"""
    user = context.get('user', None)
    deletion_requests = get_reports_by_user(user, obj,
                                            reason=Report.DELETION_REQUEST)
    disabled = not can_delete(obj, user) and deletion_requests.count() > 0
    return dict(app_label=obj._meta.app_label,
                model_name=obj._meta.module_name,
                id=obj.id,
                disabled=disabled)


@register.inclusion_tag('moderation/report_content_box_templatetag.html',
        takes_context=True)
def report_content_box(context):
    """The syntax: {% report_content_box %}"""
    return dict(types=Report.REASON_NAMES.items()[1:])
