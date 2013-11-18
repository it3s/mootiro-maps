# -*- coding:utf-8 -*-
import os
import shutil

from contextlib import contextmanager as _contextmanager
from ConfigParser import ConfigParser
import logging
logging.basicConfig(format='>> %(message)s', level=logging.DEBUG)

from fabric.state import env
from fabric.api import *
from fabric.contrib.files import exists


# FIXME: Use the upstream repo
env.komoo_repo_url = 'https://github.com/LuizArmesto/mootiro-maps.git'
env.komoo_repo_branch = 'develop'


@_contextmanager
def virtualenv():
    if not 'komoo_activate' in env or not 'komoo_project_folder' in env:
        abort('Missing remote destination.\n\n'
              'Usage: fab remote:<env> <command>')
    env.komoo_using_virtualenv = True
    activate = env.komoo_activate
    with env.cd(env.komoo_project_folder), prefix(activate):
        yield


def virtualenv_(func):
    '''Decorator to run commands on a remote virtualenv.'''
    if getattr(env, 'komoo_using_virtualenv', False):
        # already on a remote virtualenv
        wrapped_func = func
    else:
        def wrapped_func(*a, **kw):
            with virtualenv():
                return func(*a, **kw)
    return wrapped_func


def servers_conf(env_):
    defaults = {
        'dbname': 'mootiro_maps',
        'dbuser': 'maps',
        'virtualenv': 'mootiro_maps',
        'server_port': '8001',
        'apache_conf': 'maps',
        'maintenance_apache_conf': 'maps_maintenance'
    }
    required = ['type', 'hosts', 'dir', 'django_settings']
    # Lets parse the config file to get the env attributes.
    conf = ConfigParser(defaults)
    conf.read(os.path.join(env.fabfile_dir, 'servers.conf'))

    available = conf.sections()

    # Defining some messages to be displayed to user.
    usage_msg = 'Usage: fab use:<env> <command>'
    available_msg = (
        'The available envs are: "{envs}". '
        'To modify your environments edit the configuration file "servers.conf".'
    ).format(envs=', '.join(available))

    # The user should specify an env to use.
    if not env_:
        abort(''.join(['You should specify which "env" you want to use.\n',
              available_msg, '\n\n', usage_msg]))

    # The env should be specified in the config file.
    if env_ not in available:
        abort(''.join(['Environment not found: "{}".\n', available_msg])
                .format(env_))

    # Verify if all required options were defined.
    not_defined = [i for i in required if i not in conf.options(env_)]
    if not_defined:
        abort('There are some required options not defined for "{}": {}.\n'
              'Please, edit "servers.conf" file and fill all required options.\n'
              .format(env_, ', '.join(not_defined)))
    return conf


@task
def remote(env_=False):
    '''Setup env dict for running remote commands in a specific environment.'''
    # Loads the configuration file
    conf = servers_conf(env_)

    # Sets the configuration options to global variable `env` to be used by
    # remote tasks.

    # Using extend to allow "-H" option
    env.hosts.extend(conf.get(env_, 'hosts').split(','))
    env.komoo_env = conf.get(env_, 'type')
    env.komoo_django_settings = conf.get(env_, 'django_settings')
    env.komoo_dbname = conf.get(env_, 'dbname')
    env.komoo_dbuser = conf.get(env_, 'dbuser')
    env.komoo_virtualenv = conf.get(env_, 'virtualenv')
    env.komoo_activate = '. ~/.virtualenvs/{}/bin/activate'.format(conf.get(env_, 'virtualenv'))
    env.komoo_project_folder = conf.get(env_, 'dir')
    env.komoo_port = conf.get(env_, 'server_port')
    env.komoo_apache_conf = conf.get(env_, 'apache_conf')
    env.komoo_maintenance_apache_conf = conf.get(env_,
                                                 'maintenance_apache_conf')

    # Uses remote functions
    env.getfile = get
    env.exists = exists
    env.run = run
    env.cd = cd

    env.is_remote = True

@task(alias='local')
def local_():
    '''Setup env dict for running local commands.'''
    execute('remote', 'local')

    # Uses local functions
    env.getfile = shutil.copyfile
    env.exists = os.path.exists
    env.run = local
    env.cd = lcd

    env.is_remote = False


@task
def production():
    '''Setup env dict for running remote commands in production.'''
    execute('remote', 'production')


@task
def staging():
    '''Setup env dict for running remote commands in staging.'''
    execute('remote', 'staging')


def setup_django():
    # TODO: Verify if fabric's Django integration works.

    import os
    import sys

    FAB_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJ_DIR = os.path.abspath(os.path.join(FAB_DIR, '../mootiro_maps'))
    APP_DIR = os.path.abspath(os.path.join(PROJ_DIR, 'apps'))
    LIB_DIR = os.path.abspath(os.path.join(PROJ_DIR, 'lib'))
    SITE_ROOT = os.path.abspath(os.path.join(PROJ_DIR, '../mootiro_maps'))
    sys.path.append(PROJ_DIR)
    sys.path.append(APP_DIR)
    sys.path.append(LIB_DIR)
    sys.path.append(SITE_ROOT)
    print '---->', LIB_DIR
    from django.core.management import setup_environ
    exec 'import {} as environ'.format(env.komoo_django_settings)
    setup_environ(environ)


@task
def kill_tasks(*tasks):
    """ Kill background tasks given a list o task names """
    if not tasks:
        tasks = ['coffee', 'sass', 'elasticsearch', 'manage.py']
    for task in tasks:
        try:
            env.run(
                "ps -eo pid,args | grep %s | grep -v grep | "
                "cut -c1-6 | xargs kill" % task)
        except Exception:
            logging.warning('cannot execut kill on taks: {}'.format(task))
