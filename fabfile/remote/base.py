# -*- coding:utf-8 -*-
import os

from fabric.state import env
from fabric.api import *
from contextlib import contextmanager as _contextmanager
from ConfigParser import ConfigParser


@_contextmanager
def remote_virtualenv():
    if not 'komoo_activate' in env or not 'komoo_project_folder' in env:
        abort('Missing remote destination.\n\n'
              'Usage: fab use:<env> <command>')
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
        def wrapped_func(*a, **kw):
            with remote_virtualenv():
                return func(*a, **kw)
    return wrapped_func


def envs_conf(env_):
    defaults = {
        'dbname': 'mootiro_maps',
        'virtualenv': 'mootiro_maps',
        'server_port': '8001',
        'apache_conf': 'maps',
        'maintenance_apache_conf': 'maps_maintenance'
    }
    required = ['hosts', 'dir', 'django_settings']
    # Lets parse the config file to get the env attributes.
    conf = ConfigParser(defaults)
    conf.read(os.path.join(env.fabfile_dir, 'envs.conf'))

    available_envs = conf.sections()

    # Defining some messages to be displayed to user.
    usage_msg = 'Usage: fab use:<env> <command>'
    available_msg = (
        'The available envs are: "{envs}". '
        'To modify your environments edit the configuration file "envs.conf".'
    ).format(envs=', '.join(available_envs))

    # The user should specify an env to use.
    if not env_:
        abort(''.join(['You should specify which "env" you want to use.\n',
              available_msg, '\n\n', usage_msg]))

    # The env should be specified in the config file.
    if env_ not in available_envs:
        abort(''.join(['Environment not found: "{}".\n', available_msg])
                .format(env_))

    # Verify if all required options were defined.
    not_defined = [i for i in required if i not in conf.options(env_)]
    if not_defined:
        abort('There are some required options not defined for "{}": {}.\n'
              'Please, edit "envs.conf" file and fill all required options.\n'
              .format(env_, ', '.join(not_defined)))
    return conf


@task
def use(env_=False):
    '''Setup env dict for running remote commands in a specific environment.'''
    # Loads the configuration file
    conf = envs_conf(env_)

    # Sets the configuration options to global variable `env` to be used by
    # remote tasks.

    # Using extend to allow "-H" option
    env.hosts.extend(conf.get(env_, 'hosts').split(','))
    env.komoo_env = env_
    env.komoo_django_settings = '--settings={}'.format(
        conf.get(env_, 'django_settings'))
    env.komoo_dbname = conf.get(env_, 'dbname')
    env.komoo_activate = 'workon {}'.format(conf.get(env_, 'virtualenv'))
    env.komoo_project_folder = conf.get(env_, 'dir')
    env.komoo_port = conf.get(env_, 'server_port')
    env.komoo_apache_conf = conf.get(env_, 'apache_conf')
    env.komoo_maintenance_apache_conf = conf.get(env_,
                                                 'maintenance_apache_conf')


@task
def production():
    '''Setup env dict for running remote commands in production.'''
    warn('Deprecated: use "fab use:production <command>".')
    execute('use', 'production')


@task
def staging():
    '''Setup env dict for running remote commands in staging.'''
    warn('Deprecated: use "fab use:staging <command>".')
    execute('use', 'staging')
