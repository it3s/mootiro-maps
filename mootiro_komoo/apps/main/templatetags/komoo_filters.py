# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import re
from datetime import date, datetime, timedelta

from django import template
from django.conf import settings
from django.template import defaultfilters
from django.utils.encoding import force_unicode
from django.utils.formats import number_format
from django.utils.translation import pgettext, ungettext, ugettext as _

register = template.Library()


# Code from django.contrib.humanize.templatetags
@register.filter
def naturaltime(value):
    """
    For date and time values shows how many seconds, minutes or hours ago
    compared to current timestamp returns representing string.
    """
    if not isinstance(value, date): # datetime is a subclass of date
        return value

    # These two lines below are only available in django 1.4
    # from django.utils.timezone import is_aware, utc
    # now = datetime.now(utc if is_aware(value) else None)
    now = datetime.now()
    if value < now:
        delta = now - value
        if delta.days > 30:
            return pgettext(
                'more than 1 month ago', 'on %(date)s at %(time)s'
            ) % {
                'date': value.strftime("%d/%m/%Y"),
                'time': value.strftime("%H:%M")
            }
        elif delta.days != 0:
            return pgettext(
                'naturaltime', '%(delta)s ago'
            ) % {'delta': defaultfilters.timesince(value)}
        elif delta.seconds == 0:
            return _('now')
        elif delta.seconds < 60:
            return ungettext(
                'a second ago', '%(count)s seconds ago', delta.seconds
            ) % {'count': delta.seconds}
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return ungettext(
                'a minute ago', '%(count)s minutes ago', count
            ) % {'count': count}
        else:
            count = delta.seconds // 60 // 60
            return ungettext(
                'an hour ago', '%(count)s hours ago', count
            ) % {'count': count}
    else:
        delta = value - now
        if delta.days != 0:
            return pgettext(
                'naturaltime', '%(delta)s from now'
            ) % {'delta': defaultfilters.timeuntil(value)}
        elif delta.seconds == 0:
            return _('now')
        elif delta.seconds < 60:
            return ungettext(
                'a second from now', '%(count)s seconds from now', delta.seconds
            ) % {'count': delta.seconds}
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return ungettext(
                'a minute from now', '%(count)s minutes from now', count
            ) % {'count': count}
        else:
            count = delta.seconds // 60 // 60
            return ungettext(
                'an hour from now', '%(count)s hours from now', count
            ) % {'count': count}
