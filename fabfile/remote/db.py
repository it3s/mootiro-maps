# -*- coding:utf-8 -*-
import os

from fabric.api import *
from fabric.contrib.files import exists
from datetime import datetime

from .base import remote


def DBFILE():
    return 'backupdb_{}_{}.sql'.format(env.komoo_env,
                        datetime.now().strftime('%Y_%m_%d'))


@task
@remote
def backup_db(forced=False):
    '''Dumps remote database and stores it in backups folder.'''
    remote_path = '{}/backups/{}'.format(env.komoo_project_folder, DBFILE())
    if exists(remote_path):
        if not forced:
            return remote_path
    run('pg_dump --no-privileges --no-owner {} > {}'.format(env.komoo_dbname,
        remote_path))
    return remote_path


@task
@remote
def load_data(file_):
    '''Loads data from json file.'''
    run('psql {} < {}'.format(env.komoo_dbname, file_))


@task
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


@task
@remote
def migrate_database(script):
    '''Dumps database to a file, runs migration script and loads it back.'''
    input_file = backup_db()
    output_file = input_file + ' (migrated)'
    run('python {script} {inp} {out}'.format(script=script, inp=input_file,
            out=output_file))
    load_data(output_file)
