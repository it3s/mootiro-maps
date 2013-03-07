# -*- coding:utf-8 -*-
from fabric.api import *
from fabric.contrib.files import exists
from fabric.colors import yellow

from .base import remote_virtualenv


__all__ = ('up', 'down', 'restart')


def _setup_supervisor():
    # make sure supervisord is running
    sock_file = '{}/supervisor/supervisor.sock'.format(env.komoo_project_folder)
    if not exists(sock_file):
        with remote_virtualenv():
            run('supervisord -c supervisor/{}.conf'.format(env.komoo_env))


def up():
    '''Start remote application server.'''
    _setup_supervisor()
    with remote_virtualenv():
        run('supervisorctl -c supervisor/{env}.conf start {env}:' \
            .format(env=env.komoo_env))
    print yellow('Success, but it may take 1 minute for the server to go up.')


def down():
    '''Stop remote application server.'''
    _setup_supervisor()
    with remote_virtualenv():
        run('supervisorctl -c supervisor/{env}.conf stop {env}:' \
            .format(env=env.komoo_env))


def restart():
    '''Restart remote application server.'''
    _setup_supervisor()
    with remote_virtualenv():
        run('supervisorctl -c supervisor/{env}.conf restart {env}:' \
            .format(env=env.komoo_env))
