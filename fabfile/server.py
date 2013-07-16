# -*- coding:utf-8 -*-

from fabric.state import env
from fabric.api import *
from fabric.contrib.files import exists
from fabric.colors import yellow

from .base import virtualenv


__all__ = ('start', 'stop', 'restart')


def _setup_supervisor():
    # make sure supervisord is running
    sock_file = ('{}/supervisor/supervisor.sock'
                 ).format(env.komoo_project_folder)
    if not exists(sock_file):
        with virtualenv(), env.cd('mootiro_maps'):
            env.run('supervisord -c {}/supervisor/{}.conf'.format(
                env.komoo_project_folder, env.komoo_env))


@task(alias='up')
def start():
    '''Start remote application server.'''
    _setup_supervisor()
    with virtualenv(), env.cd('mootiro_maps'):
        env.run('supervisorctl -c {dir}/supervisor/{env}.conf start {env}:'
                .format(env=env.komoo_env, dir=env.komoo_project_folder))

    # maintenance page goes down
    #sudo('a2dissite {komoo_maintenance_apache_conf}; '
    #     'a2ensite {komoo_apache_conf}; '
    #     'service apache2 reload'.format(**env))

    print yellow('Success, but it may take 1 minute for the server to go up.')


@task(alias='down')
def stop():
    '''Stop remote application server.'''
    _setup_supervisor()
    with virtualenv(), env.cd('mootiro_maps'):
        env.run('supervisorctl -c {dir}/supervisor/{env}.conf stop {env}:'
                .format(env=env.komoo_env, dir=env.komoo_project_folder))

    # maintenance page goes up
    #sudo('a2dissite {komoo_apache_conf}; '
    #     'a2ensite {komoo_maintenance_apache_conf}; '
    #     'service apache2 reload'.format(**env))


@task
def restart():
    '''Restart remote application server.'''
    _setup_supervisor()
    with virtualenv(), env.cd('mootiro_maps'):
        env.run('supervisorctl -c {dir}/supervisor/{env}.conf restart {env}:'
                .format(env=env.komoo_env, dir=env.komoo_project_folder))
