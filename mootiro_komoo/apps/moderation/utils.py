# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

import datetime

from django.conf import settings
from moderation.models import Moderation


def can_delete(obj, user):
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
