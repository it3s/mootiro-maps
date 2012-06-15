"""
Django does not recognize
This module must be explicit imported
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


def _new_update_data(instance):
    data = {
        'title': instance.name,
        'date': instance.creation_date,
        'typ': Update.TYPES[0][0],
        'object_type': instance._meta.verbose_name,
        'users': instance.creator.username,
    }

    if getattr(instance, 'community', None):
        data['communities'] = instance.community.all()

    return data


@receiver(post_save, sender=Investment, dispatch_uid="log_update")
@receiver(post_save, sender=Resource, dispatch_uid="log_update")
@receiver(post_save, sender=Organization, dispatch_uid="log_update")
@receiver(post_save, sender=Proposal, dispatch_uid="log_update")
@receiver(post_save, sender=Need, dispatch_uid="log_update")
@receiver(post_save, sender=Community, dispatch_uid="community_post_save")
def create_update(sender, **kwargs):
    created = kwargs["created"]
    instance = kwargs["instance"]
    creator = getattr(instance, 'creator', None)

    if created and creator:
        data = _new_update_data(instance)
        update = Update(**data)
        update.save()
    else:
        # TODO: handle slug changes
        pass
