# -*- coding:utf-8 -*-
from fabric.api import *
from contextlib import contextmanager as _contextmanager


@_contextmanager
def virtualenv():
    if not 'komoo_activate' in env or not 'komoo_project_folder' in env:
        abort('Missing remote destination.\n'
              'Usage: fab (production|staging) <command>.')
    env.komoo_virtualenv = True
    with cd(env.komoo_project_folder):
        with prefix(env.komoo_activate):
            yield


def remote(func):
    '''Decorator to run commands on a remote virtualenv.'''
    if getattr(env, 'komoo_virtualenv', False):
        # already on a remote virtualenv
        wrapped_func = func
    else:
        def wrapped_func():
            with virtualenv():
                return func()
    return wrapped_func


def production():
    '''Setup env dict for running remote commands in production.'''
    env.hosts = ['maps.mootiro.org']
    env.komoo_env = 'production'
    env.komoo_django_settings = '--settings=settings.production'
    env.komoo_activate = 'source /home/login/.virtualenvs/mootiro_maps_env/bin/activate'
    env.komoo_project_folder = '/home/login/mootiro_maps/mootiro-maps/mootiro_komoo'
    env.komoo_port = '8001'


def staging():
    '''Setup env dict for running remote commands in staging.'''
    env.hosts = ['maps.mootiro.org']
    env.komoo_env = 'staging'
    env.komoo_django_settings = '--settings=settings.staging'
    env.komoo_activate = 'source /home/login/.virtualenvs/mootiro_maps_staging_env/bin/activate'
    env.komoo_project_folder = '/home/login/mootiro_maps_staging/mootiro-maps/mootiro_komoo'
    env.komoo_port = '5001'
