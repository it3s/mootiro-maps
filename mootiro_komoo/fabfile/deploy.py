# -*- coding:utf-8 -*-
import os

from contextlib import contextmanager as _contextmanager
from fabric.api import *
from fabric.colors import cyan, red, yellow, green
from fabric.contrib.files import exists
from fabric.contrib.console import confirm

from .old_fabfile import sync_all, run as runapp


# __all__ = ('production', 'staging', 'deploy')

def production():
    '''Setup env dict for running remote commands in production.'''
    env.name = 'production'
    env.hosts = ['maps.mootiro.org']
    env.django_settings = '--settings=settings.production'
    env.activate = 'source /home/login/.virtualenvs/mootiro_maps_env/bin/activate'
    env.project_folder = '/home/login/mootiro_maps/mootiro-maps/mootiro_komoo'


def staging():
    '''Setup env dict for running remote commands in staging.'''
    env.name = 'staging'
    env.hosts = ['maps.mootiro.org']
    env.django_settings = '--settings=settings.staging'
    env.activate = 'source /home/login/.virtualenvs/mootiro_maps_staging_env/bin/activate'
    env.project_folder = '/home/login/mootiro_maps_staging/mootiro-maps/mootiro_komoo'


@_contextmanager
def virtualenv():
    if not 'activate' in env or not 'project_folder' in env:
        abort('Missing remote destination.\n'
              'Usage: fab (production|staging) <command>.')

    with cd(env.project_folder):
        with prefix(env.activate):
            yield


DBFILE = 'backupdb.json'

def deploy():
    '''Deploy application to staging or production.'''
    print(cyan('Local deploy simulation\n'))
    print('Getting remote database copy...'))
    get_database_dump()

    pyfile = prompt("Python script to do migration (empty if none):")
    if pyfile:
        _migrate_database_dump(pyfile, DBFILE)

    sync_all(DBFILE)
    runapp()
    print(cyan('Deploying to remote'))


def get_database_dump():
    '''Dump remote database and transfers a copy of it locally.'''
    import datetime
    with virtualenv():
        filename = 'backupdb_{}_{}.json'.format(
            env.name,
            datetime.datetime.now().strftime('%Y_%m_%d')
        )
        local_path = DBFILE
        remote_path = '{}/backups/{}'.format(env.project_folder, filename)
        if os.path.exists(local_path):
            if not confirm('Backup exists at {}. Do you want to overwrite it?'\
                    .format(local_path)):
                return
        if not exists(remote_path):
            run('python manage.py dumpdata {} > {}'.format(
                    env.django_settings, remote_path))
        get(remote_path, local_path)


def _migrate_database_dump(script, json_file=DBFILE):
    '''Runs migration script in backupdb.json'''
    if not os.path.exists(json_file):
        abort('DB dump file {} does not exists. Aborting.'.format(json_file))

    local('python {script} {inp} {out}'.format(script=script,
            inp=json_file, out='temp.json'))



### Simulação Local ###
# [ ] dumpdata do banco em produção
# [ ] scp para baixar cópia
#     [ ] verificar se já existe um backup recente
# [ ] script de migração do dump no json (qual?)
# [ ] script ad-hoc de atualização
# [ ] sync_all:'backup migrado'
#     [ ] se falhar, aborta
# [ ] testar run
#     [ ] se falhar, aborta
# [ ] git tag (qual?)
