# -*- coding:utf-8 -*-

from fabric.state import env
from fabric.api import *
from fabric.colors import cyan, yellow
from fabric.contrib.console import confirm
from fabric.utils import abort

from .base import virtualenv
from .server import start as server_start, stop as server_stop
from .db import backup as db_backup


__all__ = ('deploy',)


@task(default=True)
def deploy(migration=False):
    '''Deploy application to staging or production.'''

    # gathering deploy information
    d = {}
    with quiet():
        d['server'] = env.komoo_env
        with virtualenv():
            d['from_commit'] = env.run('git rev-parse --short HEAD')
        d['branch'] = local('git rev-parse --abbrev-ref HEAD', capture=True)
        d['to_commit'] = local('git rev-parse --short HEAD', capture=True)
        d['tag'], past, cm = local('git describe --tags --long',
                                   capture=True).split('-')
        d['migration'] = bool(migration)

    print
    print cyan('======= Deploy Information =======')
    print 'target server: {}'.format(d['server'])
    print 'from commit: {}'.format(d['from_commit'])
    s = 'current branch: {}'.format(d['branch'])
    if d['server'] == 'production' and d['branch'] != 'stable':
        s += yellow(' (should be stable)')
    elif d['server'] == 'staging' and d['branch'] != 'staging':
        s += yellow(' (should be staging)')
    print s
    print 'to commit: {}'.format(d['to_commit'])
    print 'stop for db migration: {}'.format('yes' if d['migration'] else 'no')
    if d['server'] == 'production':
        past = int(past)
        if past > 0:  # tag is already old
            d['tag'] = 'none ' + yellow('(should not be empty!)')
        print 'git tag: {}'.format(d['tag'])
    print

    if not confirm('Proceed deploy?', default=False):
        return

    if d['server'] == 'staging':
        deploy_to_staging(d)
    if d['server'] == 'production':
        deploy_to_production(d)


def deploy_to_staging(deploy_info):
    '''Staging deploy strategy.'''
    with quiet():
        server_stop()
    checkout(deploy_info['to_commit'])
    install_requirements()
    collectstatic()
    if deploy_info['migration']:
        print yellow("We've stopped to do db migration now. After you're "
                     "done run 'fab remote:{} start'\n".
                     format(deploy_info['server']))
        exit()
    server_start()


def deploy_to_production(deploy_info):
    '''Production deploy strategy.'''
    with quiet():
        server_stop()
    db_backup()
    checkout(deploy_info['to_commit'])
    install_requirements()
    collectstatic()
    if deploy_info['migration']:
        print yellow("We've stopped to do db migration now. After you're "
                     "done run 'fab remote:{} start'\n".
                     format(deploy_info['server']))
        exit()
    server_start()


@task
def checkout(rev):
    '''Puts remote repository on a specific revision (tag or commit).'''
    with virtualenv():
        uncommitted = bool(env.run('git diff --shortstat'))
        if uncommitted:
            if confirm('You have uncommitted changes on your remote repo.'
                       'Trash them away?', default=False):
                env.run('git reset --hard')
            else:
                diff = run('git diff')
                abort('git diff output:\n\n{}'.format(diff))
        env.run('git fetch && git checkout {}'.format(rev))


@task
def collectstatic():
    '''Runs static files collector'''
    with virtualenv(), env.cd('mootiro_maps'):
        env.run('python manage.py collectstatic --settings={}'
                .format(env.komoo_django_settings))


@task
def install_requirements():
    with virtualenv(), env.cd('mootiro_maps'):
        env.run('pip install -r settings/requirements.txt')
