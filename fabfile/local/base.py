#! /usr/bin/env python
# -*- coding:utf-8 -*-

import logging
logging.basicConfig(format='>> %(message)s', level=logging.DEBUG)

from fabric.api import local

#env.hosts = ['me@example.com:22']

django_settings = {
    'dev': '--settings=settings.development',
    'stage': '--settings=settings.staging',
    'prod': '--settings=settings.production'
}
env_ = 'dev'


def _set_env(type_):
    global env_
    env_ = type_


def dev():
    _set_env('dev')


def stage():
    _set_env('stage')


def prod():
    _set_env('prod')


def setup_django():
    import os
    import sys

    FAB_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJ_DIR = os.path.abspath(os.path.join(FAB_DIR, '../../mootiro_maps'))
    APP_DIR = os.path.abspath(os.path.join(PROJ_DIR, 'apps'))
    LIB_DIR = os.path.abspath(os.path.join(PROJ_DIR, 'lib'))
    SITE_ROOT = os.path.abspath(os.path.join(PROJ_DIR, '../../mootiro_maps'))
    sys.path.append(PROJ_DIR)
    sys.path.append(APP_DIR)
    sys.path.append(LIB_DIR)
    sys.path.append(SITE_ROOT)
    from django.core.management import setup_environ
    env_name = {'dev': 'development', 'stage': 'staging', 'prod': 'production'}
    environ = None
    exec 'from settings import {} as environ'.format(env_name[env_])
    setup_environ(environ)


def kill_tasks(*tasks):
    """ Kill background tasks given a list o task names """
    if not tasks:
        tasks = ['coffee', 'sass', 'elasticsearch', 'manage.py']
    for task in tasks:
        try:
            local(
                "ps -eo pid,args | grep %s | grep -v grep | "
                "cut -c1-6 | xargs kill" % task)
        except Exception:
            logging.warning('cannot execut kill on taks: {}'.format(task))
