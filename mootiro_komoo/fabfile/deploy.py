# -*- coding:utf-8 -*-
from contextlib import contextmanager as _contextmanager
from fabric.api import *
from fabric.contrib.files import exists


__all__ = ('production', 'staging', 'deploy')

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


def deploy():
    '''Deploy application to staging or production.'''

    get_database_dump()


def get_database_dump():
    '''Dump remote database and transfers a copy of it locally.'''
    import datetime
    with virtualenv():
        remote_path = '{}/backups/backupdb_{}_{}.json'.format(
            env.project_folder,
            env.name,
            datetime.datetime.now().strftime('%Y_%m_%d')
        )
        if not exists(remote_path):
            run('python manage.py dumpdata {} > {}'.format(
                    env.django_settings, remote_path))
        get(remote_path, './backups')





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
