# -*- coding:utf-8 -*-
from fabric.api import *
from contextlib import contextmanager as _contextmanager


# TODO: move this to a remote/ package

@_contextmanager
def virtualenv():
    if not 'komoo_activate' in env or not 'komoo_project_folder' in env:
        abort('Missing remote destination.\n'
              'Usage: fab (production|staging) <command>.')

    with cd(env.komoo_project_folder):
        with prefix(env.komoo_activate):
            yield


def remote(func):
    def wrapped_func():
        with virtualenv():
            func()
    return wrapped_func


def production():
    '''Setup env dict for running remote commands in production.'''
    env.hosts = ['maps.mootiro.org']
    env.komoo_name = 'production'
    env.komoo_django_settings = '--settings=settings.production'
    env.komoo_activate = 'source /home/login/.virtualenvs/mootiro_maps_env/bin/activate'
    env.komoo_project_folder = '/home/login/mootiro_maps/mootiro-maps/mootiro_komoo'
    env.komoo_port = '8001'


def staging():
    '''Setup env dict for running remote commands in staging.'''
    env.hosts = ['maps.mootiro.org']
    env.komoo_name = 'staging'
    env.komoo_django_settings = '--settings=settings.staging'
    env.komoo_activate = 'source /home/login/.virtualenvs/mootiro_maps_staging_env/bin/activate'
    env.komoo_project_folder = '/home/login/mootiro_maps_staging/mootiro-maps/mootiro_komoo'
    env.komoo_port = '5001'
