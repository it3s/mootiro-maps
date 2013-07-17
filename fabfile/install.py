#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.state import env
from fabric.api import task, execute, warn, sudo, run, cd, prefix

from .base import virtualenv as virtualenv_cm
from .check import (dir as check_dir, repo as check_repo,
        virtualenv as check_virtualenv)


@task
def elasticsearch():
    """ download and place elastic search on the lib folder """
    # FIXME: Hard coded version is evil.
    with virtualenv_cm():
        env.run(''
                'wget -P lib/ http://download.elasticsearch.org/elasticsearch/'
                'elasticsearch/elasticsearch-0.20.5.tar.gz;'
                'tar xzvf lib/elasticsearch-0.20.5.tar.gz -C lib/;'
                'mv lib/elasticsearch-0.20.5 lib/elasticsearch;'
                'rm lib/elasticsearch-0.20.5.tar.gz;'
                )


@task(default=True)
def all():
    execute('install.dependencies')
    execute('install.virtualenv')
    execute('install.project')
    execute('install.requirements')
    execute('install.patch')
    execute('install.elasticsearch')


@task(aliases=['develop', 'development'])
def dev():
    execute('install.all')


@task(alias='django_patch')
def patch():
    """
    build env_ironment: pip install everything + patch django for postgis
    encoding problem on postgres 9.1
    """
    with virtualenv_cm():
        env.run("patch -p0 `which python | "
                "sed -e 's/bin\/python$/lib\/python2.7\/site-packages\/django\/"
                "contrib\/gis\/db\/backends\/postgis\/adapter.py/'` "
                "docs/postgis-adapter-2.patch")


@task
def requirements():
    with virtualenv_cm(), env.cd('mootiro_maps'):
        env.run('pip install -r settings/requirements.txt')


@task
def project():
    if not env.is_remote:
        warn('Can\'t execute task "install.project" locally.')
        return
    if not check_dir():
        sudo('mkdir -p {}'.format(env.komoo_project_folder))
        sudo('chown {user}:{user} {dir}'.format(user=env.user,
                                                dir=env.komoo_project_folder))
    if not check_repo():
        with cd(env.komoo_project_folder):
            run('git clone {} .'.format(env.komoo_repo_url))
            run('git checkout -b {branch} --track origin/{branch}'
                .format(branch=env.komoo_repo_branch))


@task
def virtualenv():
    if not check_virtualenv():
        with prefix('. /etc/bash_completion.d/virtualenvwrapper'):
            env.run('mkvirtualenv {}'.format(env.komoo_virtualenv))


@task(alias='dependencies')
def deps():
    if not env.is_remote:
        warn('Can\'t execute task "install.dependencies" locally.')
        return
    pkgs = ['virtualenvwrapper', 'git', 'python-dev',
            'postgresql-9.1', 'postgresql-9.1-postgis',
            'postgresql-server-dev-9.1',
            'libev4', 'libev-dev', 'libevent-2.0-5', 'libevent-dev'
            ]
    sudo('apt-get update')
    sudo('apt-get install {} -y'.format(' '.join(pkgs)))
