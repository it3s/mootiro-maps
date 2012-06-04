# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

import datetime
from smtplib import SMTPException

from django.utils.translation import ugettext as _
from django.core.mail import mail_admins
from django.core.urlresolvers import reverse
from django.conf import settings
from moderation.models import Moderation, Report


logger = logging.getLogger(__name__)


def can_delete(obj, user):
    return False
    """Verify if the object can be deketed by user"""
    if not obj or not user or not user.is_authenticated:
        return False

    now = datetime.datetime.now()
    delta = now - obj.creation_date
    hours = delta.days * 24. + delta.seconds / 3600.
    if user.is_superuser or \
            (hours <= settings.DELETE_HOURS and obj.creator == user):
        return True

    return False


def delete_object(obj):
    """Delete the object and the related moderation object"""
    moderation = Moderation.objects.get_for_object(obj)
    if moderation:
        moderation.delete()
    obj.delete()


def get_reports_by_user(user, obj=None):
    """Get reports sent by user"""
    if user.is_anonymous():
        return []
    if obj:
        moderation = Moderation.objects.get_for_object_or_create(obj)
        reports = Report.objects.filter(user=user, reason__gt=0,
                                        moderation=moderation).all()
    else:
        reports = Report.objects.filter(user=user).all()
    return reports


def create_report(*args, **kwargs):
    obj = kwargs['obj']
    user = kwargs['user']
    reason = kwargs['reason']
    comment = kwargs['comment']

    moderation = Moderation.objects.get_for_object_or_create(obj)

    report = Report(moderation=moderation, reason=reason,
            comment=comment, user=user)
    report.save()

    try:
        view_url = obj.view_url
    except AttributeError:
        view_url = 'none'
        if hasattr(obj, 'content_object') and \
                hasattr(obj.content_object, 'view_url'):
            view_url = obj.content_object.view_url

    admin_url = reverse('admin:{}_{}_change'.format(obj._meta.app_label,
                                                    obj._meta.module_name),
            args=(obj.id, ))
    body = _("""
Content: {0}
Content type: {1}
Content id: {2}
Content url: {3}
Admin url: {4}
Reporter: {5} (id: {6}, email: {7})
Reason: {8}
Comment: {9}
    """).format(obj, moderation.content_type, obj.id, view_url, admin_url,
            user, user.id, user.email, report.reason_name, comment)

    try:
        mail_admins(_('Content report'), body, fail_silently=False)
    except SMTPException, e:
        logger.debug('An error occurred while sending email ' \
                'to admin : {}'.format(e))
    return report

