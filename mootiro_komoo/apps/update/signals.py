#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Callback signals that creates new updates (instances of Update class) as users
interacts with the system.
"""

from __future__ import unicode_literals  # unicode by default

from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from .models import Update
from community.models import Community
from need.models import Need
from proposal.models import Proposal
from organization.models import Organization
from komoo_resource.models import Resource
from investment.models import Investment
from komoo_comments.models import Comment


create_update = Signal(providing_args=["user", "instance", "type"])


# Community, Need, Organization, Resource
@receiver(create_update, sender=Community)
@receiver(create_update, sender=Need)
@receiver(create_update, sender=Organization)
@receiver(create_update, sender=Resource)
def create_add_edit_update(sender, **kwargs):
    instance = kwargs["instance"]
    data = {
        'instances': [instance],
        'object_id': instance.id,
        'object_type': instance._meta.verbose_name,
        'type': kwargs["type"],
        'users': [kwargs["user"].username],
        'comments_count': Comment.comments_count_for(instance),
    }
    if getattr(instance, 'community', None):
        data['communities'] = instance.community.all()

    update = Update(**data)
    update.save()


# Proposal
@receiver(create_update, sender=Proposal)
def create_add_edit_update_for_proposal(sender, **kwargs):
    proposal = kwargs["instance"]
    need = proposal.need
    data = {
        'instances': [proposal, need],
        'object_id': proposal.id,
        'object_type': proposal._meta.verbose_name,
        'type': kwargs["type"],
        'users': [kwargs["user"].username],
        'comments_count': Comment.comments_count_for(proposal),
    }
    if getattr(need, 'community', None):
        data['communities'] = need.community.all()
    
    update = Update(**data)
    update.save()


@receiver(create_update, sender=Comment)
def create_discussion_update(sender, **kwargs):
    comment = kwargs["instance"]
    instance = comment.content_object

    discussion_update = Update.get_recent_discussion_for(instance)
    if discussion_update:
        update = discussion_update
        people = update.users
        if comment.author.username not in people:
            people.append(comment.author.username)
            update.users = people
    else:
        data = {
            'instances': [instance],
            'object_id': instance.id,
            'object_type': instance._meta.verbose_name,
            'type': Update.DISCUSSION,
            'users': [comment.author.username],
            'comments_count': Comment.comments_count_for(instance),
        }
        if type(instance) == Proposal:
            data['instances'] = [instances, instances.need]
        update = Update(**data)

    if getattr(instance, 'community', None):
        update.communities = instance.community.all()

    update.comments_count = Comment.comments_count_for(instance)
    update.save()
