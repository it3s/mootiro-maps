#! /usr/bin/env python
# -*- coding:utf-8 -*-

import logging
from fabric.api import local

from .base import django_settings, env_, setup_django
from .service import run_celery, run_datalog, run_elasticsearch


def run(port=8001):
    """Runs django's development server"""
    run_celery()
    run_datalog()
    run_elasticsearch(bg='true')
    if env_ != 'dev':
        local(
            'python mootiro_maps/manage.py run_gunicorn --workers=2 '
            '--bind=127.0.0.1:{} {}'.format(port, django_settings[env_]))
    else:
        local('python mootiro_maps/manage.py runserver --insecure {} {}'
              .format(port, django_settings[env_]))


def shell():
    """Launches Django interactive shell"""
    local('python mootiro_maps/manage.py shell {}'.format(
        django_settings[env_]))


def supercow(email=None):
    """Grants admin supercow rights to a user."""
    setup_django()
    from authentication.models import User
    user = User.objects.get(email=email)
    user.is_admin = True
    user.save()
    logging.info('success')


def initial_revisions():
    """
    load initial revisions for django-revisions module
    should run only once when installed/or when loaded a new app/model
    """
    local('python mootiro_maps/manage.py createinitialrevisions {}'
          .format(django_settings[env_]))


def clean_media_files():
    """removes all media uploaded files"""
    media_apps_list = ['upload', ]
    for app in media_apps_list:
        try:
            local('rm  -rf media/{}/'.format(app))
        except Exception as err:
            logging.error(err)


def populate_history():
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
