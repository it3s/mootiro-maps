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
from komoo_project.models import Project
from komoo_comments.models import Comment

create_update = Signal(providing_args=["user", "instance", "type"])


def _create_the_update(instances, communities, **kwargs):
    instance = kwargs["instance"]
    user = kwargs["user"]
    type_ = kwargs["type"]

    ago = dict(days=1) if (type_ == Update.DISCUSSION) else dict(hours=12)
    recent_update = Update.get_recent_for(instance, type_, **ago)
    if recent_update:
        update = recent_update
        people = update.users
        if user.username not in people:
            people.insert(0, user.username)
            update.users = people
    else:
        data = {
            'object_id': instance.id,
            'object_type': instance._meta.verbose_name,
            'type': type_,
            'users': [user.username],
        }
        update = Update(**data)

    update.instances = instances
    update.communities = communities
    update.comments_count = Comment.comments_count_for(instance)
    update.save()


# Community
@receiver(create_update, sender=Community)
def create_community_update(sender, **kwargs):
    instance = kwargs["instance"]
    instances = [instance]
    communities = []
    _create_the_update(instances, communities, **kwargs)


# Need, Organization, Resource
@receiver(create_update, sender=Need)
@receiver(create_update, sender=Organization)
@receiver(create_update, sender=Resource)
def create_need_org_res_update(sender, **kwargs):
    instance = kwargs["instance"]
    instances = [instance]
    communities = instance.community.all()
    _create_the_update(instances, communities, **kwargs)


# Proposal
def _proposal_instances(proposal):
    return [proposal, proposal.need]


@receiver(create_update, sender=Proposal)
def create_proposal_update(sender, **kwargs):
    proposal = kwargs["instance"]
    instances = _proposal_instances(proposal)
    communities = proposal.need.community.all()
    _create_the_update(instances, communities, **kwargs)


@receiver(create_update, sender=Project)
def create_proj_update(sender, **kwargs):
    instance = kwargs["instance"]
    instances = [instance]
    communities = []
    _create_the_update(instances, communities, **kwargs)


# Comment
@receiver(create_update, sender=Comment)
def create_discussion_update(sender, **kwargs):
    instance = kwargs["instance"].content_object
    kwargs["instance"] = instance

    if type(instance) == Proposal:
        instances = _proposal_instances(instance)
    else:
        instances = [instance]

    if type(instance) == Community:
        communities = []
    elif hasattr(instance, 'community'):
        communities = instance.community.all()
    else:
        return None

    _create_the_update(instances, communities, **kwargs)
