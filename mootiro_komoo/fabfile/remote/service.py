# -*- coding:utf-8 -*-
from fabric.api import *
from .base import remote_virtualenv
from fabric.colors import yellow


__all__ = ('up', 'down', 'restart')


def setup_supervisor():
    with quiet():
        # make sure supervisord is running
        run('supervisord -c supervisor/{}.conf'.format(env.komoo_env))


def up():
    '''Start remote application server.'''
    setup_supervisor()
    with remote_virtualenv():
        run('supervisorctl -c supervisor/{env}.conf start {env}' \
            .format(env=env.komoo_env))
    print yellow('Success, but it may take 1 minute for the server to go up.')


def down():
    '''Stop remote application server.'''
    setup_supervisor()
    with remote_virtualenv():
        run('supervisorctl -c supervisor/{env}.conf stop {env}' \
            .format(env=env.komoo_env))


def restart():
    '''Restart remote application server.'''
    setup_supervisor()
    with remote_virtualenv():
        run('supervisorctl -c supervisor/{env}.conf restart {env}' \
            .format(env=env.komoo_env))
