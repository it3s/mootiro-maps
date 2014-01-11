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
