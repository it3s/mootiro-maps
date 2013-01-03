# -*- coding:utf-8 -*-
import os

from fabric.api import *
from fabric.colors import cyan, red, yellow, green
from fabric.contrib.files import exists
from fabric.contrib.console import confirm
from fabric.utils import indent

from .utils import remote, virtualenv

from .old_fabfile import sync_all, run as runapp


__all__ = ('deploy')


DBFILE = 'backupdb.json'

def simulate_deploy():
    '''Simulate locally, the application deploy to staging or production.'''
    print(cyan('Local deploy simulation\n'))
    print('Getting remote database copy...')
    db_get_dump()

    pyfile = prompt("Python script to do migration (empty if no migration):")
    if pyfile:
        _migrate_database_dump(pyfile, DBFILE)

    sync_all(DBFILE)
    runapp()


def deploy():
    '''Deploy application to staging or production.'''

    # git tag version to deploy
    ret = local('git describe --tags --long', capture=True)
    tag, past_commits, commit = ret.split('-')

    # db migration to be run
    folder = 'scripts/migrations/{}'.format(tag)
    if os.path.exists(folder):
        pyfiles = [f for f in os.listdir() if f.endswith('.py')]
        if len(pyfiles) > 1:
            abort('More than 1 migration python script in {}'.format(folder))
        migr = pyfiles[0]
    else:
        migr = None

    print
    print cyan('===== Deploy Information =====')
    print 'target version: {}'.format(tag)
    print 'commit: {}'.format(commit)
    print 'migration script: {}'.format(migr or 'no')
    if past_commits > 0:
        print yellow('Attention! Last {} commits will not be deployed!' \
                .format(past_commits))
    print

    if not confirm('Proceed deploy?', default=False):
        return

    local('git push --tags')

    with virtualenv():
        current_remote_commit = run('git rev-parse HEAD')
    
    down()
    db_backup()

    with virtualenv():
        run('git fetch && git checkout {} && '.format(tag))

    collectstatic()
    up()

    # [x] descobre commit atual no remoto
    # [x] derruba servidor remoto
    # [ ] sobe a foto do spock (opcional)
    # [x] faz backup do banco
    # [ ] git fetch --tags?
    # [x] git checkout tag
    # [x] collectstatic



@remote
def up():
    '''lift up remote application server.'''
    # TODO: use supervisor
    # supervisorctl -c supervisor/supervisord.conf start staging
    print
    print "THIS DOESN'T WORK! FIXME!"
    print
    run('python manage.py celeryd -B --loglevel=info {} &'\
            .format(env.komoo_django_settings))
    run('python manage.py run_gunicorn --workers=2 --bind=127.0.0.1:{} {} &'\
            .format(env.komoo_port, env.komoo_django_settings))


@remote
def down():
    '''kill running processes for remote application.'''
    # TODO: use supervisor
    with settings(warn_only=True):
        run('ps -eo pid,args | grep -E manage\.py.*{} | grep -v grep | '
            'cut -c1-6 | xargs kill'.format(env.komoo_django_settings))


@remote
def collectstatic():
    '''Runs static files collector'''
    run('python manage.py collectstatic {}'.format(env.komoo_django_settings))


# ================= DATABASE FUNCTIONS ========================================

@remote
def db_backup():
    '''Dumps remote database and stores it in backups folder.'''
    import datetime
    filename = 'backupdb_{}_{}.json'.format(
        env.komoo_name,
        datetime.datetime.now().strftime('%Y_%m_%d')
    )
    remote_path = '{}/backups/{}'.format(env.komoo_project_folder, filename)
    _dump_remote_database(remote_path)


@remote
def db_get_a_copy():
    '''Dump remote database and transfers a copy of it locally.'''
    local_path = DBFILE
    remote_path = os.path.join(env.komoo_project_folder, DBFILE)
    if os.path.exists(local_path):
        if not confirm('Backup exists at {}. Do you want to overwrite it?'\
                .format(local_path)):
            return
    _dump_remote_database(remote_path)
    get(remote_path, local_path)

    # clean up
    run('rm {}'.format(remote_path))


def _dump_remote_database(remote_path=DBFILE):
    run('python manage.py dumpdata {} > {}'.format(env.komoo_django_settings,
        remote_path))


# TODO: merge with _migrate_remote_database_dump
def _migrate_database_dump(script, json_file=DBFILE):
    '''Runs migration script in backupdb.json'''
    if not os.path.exists(json_file):
        abort('DB dump file {} does not exists. Aborting.'.format(json_file))

    local('python {script} {inp} {out}'.format(script=script,
            inp=json_file, out='temp.json'))

# TODO: merge with _migrate_database_dump
def _migrate_remote_database_dump(script, json_file=DBFILE):
    '''Runs migration script in backupdb.json'''
    if not os.path.exists(json_file):
        abort('DB dump file {} does not exists. Aborting.'.format(json_file))

    run('python {script} {inp} {out}'.format(script=script,
            inp=json_file, out='temp.json'))
