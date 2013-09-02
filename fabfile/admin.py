#! /usr/bin/env python
# -*- coding:utf-8 -*-

import logging

from fabric.state import env
from fabric.contrib.console import confirm
from fabric.api import task, abort

from .base import setup_django, virtualenv


@task
def shell():
    """Launches Django interactive shell"""
    with virtualenv(), env.cd('mootiro_maps'):
        env.run('python manage.py shell --settings={}'.format(
                env.komoo_django_settings))


@task(alias='su')
def supercow(email=None):
    """Grants admin supercow rights to a user."""
    if (env.is_remote):
        abort('You cannot grant admin rights remotely!')
    #TODO: Migrate this code to a `mange.py` command.
    setup_django()
    from authentication.models import User
    user = User.objects.get(email=email)
    user.is_admin = True
    user.save()
    logging.info('success')


@task
def initial_revisions():
    """
    load initial revisions for django-revisions module
    should run only once when installed/or when loaded a new app/model
    """
    with virtualenv(), env.cd('mootiro_maps'):
        env.run('python manage.py createinitialrevisions --settings={}'
                .format(env.komoo_django_settings))


@task
def clean_media_files():
    """removes all media uploaded files"""
    cont = confirm('Do you really want to remove permanently all media files?',
            default=False)
    if not cont:
        return

    media_apps_list = ['upload', ]
    for app in media_apps_list:
        try:
            with virtualenv():
                env.run('rm  -rf media/{}/'.format(app))
        except Exception as err:
            logging.error(err)


@task
def populate_history():
    if (env.is_remote):
        abort('You cannot populate gitory table remotely!')
    setup_django()
    import reversion
    from community.models import Community
    from need.models import Need
    from proposal.models import Proposal
    from organization.models import Organization
    from komoo_resource.models import Resource
    from investment.models import Investment

    for model in [Community, Need, Proposal, Organization, Resource,
                  Investment]:
        for obj in model.objects.all():
            versions = reversion.get_for_object(obj)
            if versions:
                last = versions[0]
                # first = versions.reverse()[0]
                if last.type == 1:  # 1 == Edition
                    obj.last_editor = last.revision.user

                    # Disable auto now
                    for field in obj._meta.local_fields:
                        if field.name == "last_update":
                            field.auto_now = False
                    obj.last_update = last.revision.date_created
                    obj.save()
