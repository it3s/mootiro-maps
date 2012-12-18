# -*- coding:utf-8 -*-
from contextlib import contextmanager as _contextmanager
from fabric.api import *
from fabric.colors import red
from fabric.contrib.console import confirm


__all__ = ('production', 'staging', 'deploy')

def production():
    '''Setup env dict for running remote commands in production.'''
    env.hosts = ['maps.mootiro.org']
    env.activate = 'source /home/login/.virtualenvs/mootiro_maps_env/bin/activate'
    env.project_folder = '/home/login/mootiro_maps/mootiro-maps/mootiro_komoo'


def staging():
    '''Setup env dict for running remote commands in staging.'''
    env.hosts = ['maps.mootiro.org']
    env.activate = 'source /home/login/.virtualenvs/mootiro_maps_staging_env/bin/activate'
    env.project_folder = '/home/login/mootiro_maps_staging/mootiro-maps/mootiro_komoo'


@_contextmanager
def virtualenv():
    with cd(env.project_folder):
        with prefix(env.activate):
            yield


def deploy():
    '''Deploy application to staging or production.'''
    if not 'activate' in env or not 'project_folder' in env:
        abort('Missing deploy destination.\n'
              'Usage: fab (production|stage) deploy.')

    with virtualenv():
        run('pip freeze')




# def deploy_to(env_='local'):
#     if env_ == 'local':
#         pass
#     elif env_ == 'stage':
#         pass
#     elif env_ == 'production':
#         config = {
#             'project_folder': '~/mootiro_maps/mootiro-maps/mootiro_komoo',
#             'virtualenv_name': 'mootiro_maps_env',
#         }
#     else:
#         abort(red('Unknown environment {} to deploy.'.format(env_)))

#     # with cd(config['project_folder']), \
#     #      # prefix('source ~/.bashrc'), \
#     #      prefix('workon {}'.format(config['virtualenv_name'])):
#     wk = 'workon {}'.format(config['virtualenv_name'])
#     print wk
#     with prefix(wk):
#         run('ls')


# def deploy():
#     deploy_to('production')


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
