# -*- coding:utf-8 -*-
import os

from fabric.api import *
from fabric.colors import cyan, red, yellow, green
from fabric.contrib.files import exists
from fabric.contrib.console import confirm

from .utils import remote, virtualenv

from .old_fabfile import sync_all, run as runapp


# __all__ = ('production', 'staging', 'deploy')


DBFILE = 'backupdb.json'

def simulate_deploy():
    '''Simulate locally, the application deploy to staging or production.'''
    print(cyan('Local deploy simulation\n'))
    print('Getting remote database copy...')
    get_database_dump()

    pyfile = prompt("Python script to do migration (empty if no migration):")
    if pyfile:
        _migrate_database_dump(pyfile, DBFILE)

    sync_all(DBFILE)
    runapp()


@remote
def deploy(git_tag=''):
    '''Deploy application to staging or production.'''

    print(cyan('Deploying\n'))
    current_remote_commit = run('git rev-parse HEAD')
    down()


@remote
def up():
    '''lift up remote application server.'''
    # TODO: use supervisor
    run('python manage.py run_gunicorn --workers=2 '
        '--bind=127.0.0.1:{} {} &'.format(env.komoo_port, env.komoo_django_settings))


@remote
def down():
    '''kill running processes for remote application.'''
    # TODO: use supervisor
    with settings(warn_only=True):
        run('ps -eo pid,args | grep -E manage\.py.*{} | grep -v grep | '
            'cut -c1-6 | xargs kill'.format(env.komoo_django_settings))



    # [x] descobre commit atual no remoto
    # [x] derruba servidor remoto
    # [ ] sobe a foto do spock (opcional)
    # [ ] faz backup do banco
    # [ ] git fetch --tags?
    # [ ] git checkout tag
    # [ ] collectstatic

# ================= DATABASE FUNCTIONS ========================================

@remote
def get_database_dump():
    '''Dump remote database and transfers a copy of it locally.'''
    import datetime
    filename = 'backupdb_{}_{}.json'.format(
        env.komoo_name,
        datetime.datetime.now().strftime('%Y_%m_%d')
    )
    local_path = DBFILE
    remote_path = '{}/backups/{}'.format(env.komoo_project_folder, filename)
    if os.path.exists(local_path):
        if not confirm('Backup exists at {}. Do you want to overwrite it?'\
                .format(local_path)):
            return
    _dump_remote_database()
    get(remote_path, local_path)

    # clean up
    run('rm {}'.format(DBFILE))


def _dump_remote_database(remote_path=DBFILE):
    run('python manage.py dumpdata {} > {}'.format(env.komoo_django_settings,
        remote_path))


def _migrate_database_dump(script, json_file=DBFILE):
    '''Runs migration script in backupdb.json'''
    if not os.path.exists(json_file):
        abort('DB dump file {} does not exists. Aborting.'.format(json_file))

    local('python {script} {inp} {out}'.format(script=script,
            inp=json_file, out='temp.json'))
