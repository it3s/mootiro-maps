# -*- coding:utf-8 -*-
from fabric.api import *
from .base import remote
from fabric.colors import yellow


@remote
def up():
    '''Start remote application server.'''
    # TODO: ensure supervisord is running!
    run('supervisorctl -c supervisor/supervisord.conf start {}'.format(env.komoo_name))
    print yellow('Success, but it may take up to 1 minute to go up.')


@remote
def down():
    '''Stop remote application server.'''
    # TODO: ensure supervisord is running!
    run('supervisorctl -c supervisor/supervisord.conf stop {}'.format(env.komoo_name))


@remote
def restart():
    '''Restart remote application server.'''
    # TODO: ensure supervisord is running!
    run('supervisorctl -c supervisor/supervisord.conf restart {}'.format(env.komoo_name))
