# -*- coding:utf-8 -*-
import os

from fabric.api import *
from fabric.contrib.files import exists
from datetime import datetime

from .base import remote


def DBFILE():
    return 'backupdb_{}_{}.json'.format(env.komoo_env,
                        datetime.now().strftime('%Y_%m_%d'))


@remote
def backup_db(forced=False):
    '''Dumps remote database and stores it in backups folder.'''
    remote_path = '{}/backups/{}'.format(env.komoo_project_folder, DBFILE())
    if exists(remote_path):
        if not forced:
            return remote_path
    run('python manage.py dumpdata {} > {}'.format(env.komoo_django_settings,
        remote_path))
    return remote_path


@remote
def load_data(json_file):
    '''Loads data from json file.'''
    run('python manage.py loaddata {} {}'.format(env.komoo_django_settings,
            json_file))


@remote
def get_a_db_copy():
    '''Backs up remote database and transfers a copy of it locally.'''
    local_path = DBFILE()
    if os.path.exists(local_path):
        if not confirm('Backup exists locally at {}. Do you want to '
                    'overwrite it?'.format(local_path)):
            return local_path
    remote_path = backup_db()
    get(remote_path, local_path)
    return local_path


@remote
def migrate_database(script):
    '''Dumps database to a file, runs migration script and loads it back.'''
    input_file = backup_db()
    output_file = input_file + ' (migrated)'
    run('python {script} {inp} {out}'.format(script=script, inp=input_file,
            out=output_file))
    load_data(output_file)
