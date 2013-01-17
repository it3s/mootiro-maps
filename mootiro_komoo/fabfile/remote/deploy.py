# -*- coding:utf-8 -*-
import os

from fabric.api import *
from fabric.colors import cyan, red, yellow, green
from fabric.contrib.files import exists
from fabric.contrib.console import confirm
from fabric.utils import indent

from .base import remote, remote_virtualenv
from .service import down, up
from .db import backup_db, migrate_database


__all__ = ('deploy',)


def deploy(migration_script=''):
    '''Deploy application to staging or production.'''

    # gathering deploy information
    d = {}
    # with quiet():
    #     d['server'] = env.komoo_env
    #     with virtualenv():
    #         d['from_commit'] = run('git rev-parse HEAD')
    #     d['branch'] = local('git rev-parse --abbrev-ref HEAD', capture=True)
    #     d['to_commit'] = local('git rev-parse HEAD', capture=True)
    #     d['tag'], past, cm = local('git describe --tags --long', capture=True).split('-')
    
    d['server'] = 'staging'
    d['from_commit'] = '1228665'
    d['branch'] = 'autodeploy'
    d['to_commit'] = '5f26199'
    d['migration_script'] = migration_script

    print
    print cyan('======= Deploy Information =======')
    print 'server: {}'.format(d['server'])
    print 'from commit: {}'.format(d['from_commit'])
    s = 'branch: {}'.format(d['branch'])
    if d['server'] == 'production' and d['branch'] != 'stable':
        s += yellow(' (should be stable)')
    elif d['server'] == 'staging' and d['branch'] != 'staging':
        s += yellow(' (should be staging)')
    print s
    print 'to commit: {}'.format(d['to_commit'])
    print 'db migration script: {}'.format(d['migration_script'] or 'no')
    if d['server'] == 'production':
        if past > 0:  # tag is already old
            d['tag'] = 'none ' + yellow('(should not be empty!)')
        print 'git tag: {}'.format(d['tag'])
    print

    if not confirm('Proceed deploy?', default=False):
        return

    if server == 'staging':
        deploy_to_staging(d)
    if server == 'production':
        deploy_to_production(d)


def deploy_to_staging(deploy_info):
    
    down()
    install_requirements()
    checkout(deploy_info['to_commit'])
    if 'migration_script' in  deploy_info:
        migrate_database(deploy_info['migration_script'])
    collectstatic()
    up()


@remote
def checkout(rev):
    '''Puts remote repository on a specific revision (tag or commit).'''
    run('git fetch && git checkout {}'.format(rev))


@remote
def collectstatic():
    '''Runs static files collector'''
    run('python manage.py collectstatic {}'.format(env.komoo_django_settings))


@remote
def install_requirements():
    run('pip install -r settings/requirements.txt')
