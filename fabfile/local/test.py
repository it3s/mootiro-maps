#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.api import local, task

from .base import logging, django_settings, env_


@task(default=True)
def test(
        apps=" ".join([
            'community', 'need', 'organization', 'proposal', 'komoo_resource',
            'investment', 'main', 'authentication', 'moderation']),
        recreate_db=False):
    """Run application tests"""
    if recreate_db:
        local('dropdb test_mootiro_maps')
    else:
        logging.info("Reusing old last test DB...")
    local('REUSE_DB=1 python mootiro_maps/manage.py test {} {} --verbosity=1'
          .format(apps, django_settings[env_]))


@task
def test_js(
        apps=" ".join(['komoo_map'])):
    """Run javascript tests"""
    # TODO fix this properly
    local('phantomjs scripts/run-qunit.js static/tests/tests.html')
