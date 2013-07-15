#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.state import env
from fabric.api import *

from .base import logging, virtualenv


@task(default=True)
def test(*args, **kwargs):
    app(*args, **kwargs)
    js(*args, **kwargs)

@task(alias='application')
def app(
        apps=" ".join([
            'community', 'need', 'organization', 'proposal', 'komoo_resource',
            'investment', 'main', 'authentication', 'moderation']),
        recreate_db=False):
    """Run application tests"""

    warn('Some tests are broken and should be fixed.')

    # TODO: Hard coded values are evil. Make db name configurable.
    if recreate_db:
        env.run('dropdb test_mootiro_maps')
    else:
        logging.info("Reusing old last test DB...")
    with virtualenv(), env.cd('mootiro_maps'):
        env.run('REUSE_DB=1 python manage.py test {} {} --verbosity=1'
                .format(apps, env.komoo_django_settings))


@task
def js(apps=" ".join(['komoo_map'])):
    """Run javascript tests"""
    with virtualenv():
        env.run('phantomjs scripts/run-qunit.js '
                'mootiro_maps/static/tests/tests.html')
