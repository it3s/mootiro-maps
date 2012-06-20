#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Callback signals that creates new updates (instances of Update class) as users
interacts with the system.

ATTENTION!
Django does not recognize signals.py so this module
must be explicit imported in __init__.py
"""

from __future__ import unicode_literals  # unicode by default

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Update
from community.models import Community
from need.models import Need
from proposal.models import Proposal
from organization.models import Organization
from komoo_resource.models import Resource
from investment.models import Investment


def _get_update_data(instance):
    data = {
        'title': instance.name,
        'link': instance.view_url,
        'object_type': instance._meta.verbose_name,
        'users': [instance.creator.username],
    }

    if getattr(instance, 'community', None):
        data['communities'] = instance.community.all()
    return data


@receiver(post_save, dispatch_uid="create_update")
def create_update(sender, **kwargs):
    """Create updates to be logged on frontpage"""

    klasses = [Community, Need, Organization, Resource]
    if sender not in klasses:
        return  # class not to log updates

    # print "= = = = CREATE UPDATE = = = ="
    # print sender
    # print kwargs
    # print ""
    # return

    instance = kwargs["instance"]
    if not hasattr(instance, 'creator') or not instance.creator:
        return  # not ready to be logged

    creator = instance.creator
    data = _get_update_data(instance)

    created = kwargs["created"]
    if created:
        data['type'] = Update.ADD
    else:
        data['type'] = Update.EDIT
        # TODO: handle slug changes

    update = Update(**data)
    update.save()
