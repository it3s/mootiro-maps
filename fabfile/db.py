#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
from datetime import datetime

from fabric.state import env
from fabric.contrib.console import confirm
from fabric.api import task, execute

from .base import logging, virtualenv, setup_django


@task
def create():
    """Create komoo database with postgis template."""
    dbname = env.komoo_dbname
    logging.info("Creating database '{}'".format(dbname))
    env.run('createdb -U {} -T template_postgis {}'.format(
        env.komoo_dbuser, dbname))


@task
def drop():
    """Drops komoo database """
    dbname = env.komoo_dbname
    logging.info("Droping database '{}'".format(dbname))
    if confirm('Do you really want to drop the database "{}"? '
               '(Please, make sure you have a backup)'.format(dbname),
               default=False):
        env.run('dropdb -U {} {}'.format(env.komoo_dbuser, dbname))


@task
def recreate():
    """Drops komoo database and recreates it with postgis template."""
    drop()
    create()


@task
def sync(create_superuser=""):
    """Runs syncdb (with no input flag by default)"""
    noinput = "" if create_superuser else "--noinput"
    with virtualenv(), env.cd('mootiro_maps'):
        env.run('python manage.py syncdb {} {}'.format(
            noinput, env.komoo_django_settings))


@task(alias='sync_all')
def syncall(data_fixtures='fixtures/backupdb.json'):
    """
    restart app and database from scratch.
    It: drops the DB, recreates it, syncdb, load_fixtures and call
    initial_revisions, also makes coffee and hugs you. :)
    """
    execute('recreate')
    execute('sync')
    execute('fix_contenttypes')
    if data_fixtures == "test":
        execute('load_fixtures', data_fixtures)
    else:
        execute('loaddata', data_fixtures)
    execute('loaddata', 'fixtures/contenttypes_fixtures.json')


@task
def dumpjson():
    """Dump DB data, for backup purposes """
    with virtualenv(), env.cd('mootiro_maps'):
        env.run('python manage.py dumpdata {} > backupdb_{}.json'.format(
            env.komoo_django_settings,
            datetime.now().strftime('%Y_%m_%d_%H_%M')))


@task
def loadfixtures(type_='system'):
    """
    load fixtures (system and test).
    usage:
      fab load_fixtures  ->  loads all files which name ends with
                             '_fixtures.json' inside the fixtures folder
                             (except for 'test_fixtures.json')
      fab load_fixtures:test  -> load only the fixtures/test_fixtures.json file
    """
    if type_ == 'test':
        fixtures = ""
        folder = 'fixtures/test'
        for fixture in os.listdir(folder):
            if (fixture.endswith('.json') and
                    fixture != 'contenttypes_fixtures.json'):

                fixtures += "{}/{} ".format(folder, fixture)
        with virtualenv(), env.cd('mootiro_maps'):
            env.run('python manage.py loaddata {} {}'.format(
                fixtures, env.komoo_django_settings))
    else:
        for fixture in os.listdir('fixtures'):
            if fixture.endswith('_fixtures.json'):
                with virtualenv(), env.cd('mootiro_maps'):
                    env.run('python manage.py loaddata fixtures/{} {}'.format(
                        fixture, env.komoo_django_settings))


@task
def loadjson(fixture_file=None):
    """
    load a single fixture file
    usage:
        fab loaddata:fixture_file_path -> loads the given fixture file to db
    """
    if fixture_file:
        with virtualenv(), env.cd('mootiro_maps'):
            env.run('python manage.py loaddata {} {}'.format(
                fixture_file, env.komoo_django_settings))
    else:
        logging.info("""
        Please provide a fixture file
        usage:
          fab loaddata:fixture_file_path -> loads the given fixture file to db
        """)


@task
def fix_contenttypes():
    """ remove auto added contenttypes from django for loading data """
    # TODO: create a "remote safe" way to do it. Maybe creating new "manage.py"
    # command. But before verify if this task remains useful.
    setup_django()
    from django.contrib.contenttypes.models import ContentType

    logging.info('cleaning contenttypes ... ')
    ContentType.objects.all().delete()
    execute('loaddata', 'fixtures/contenttypes_fixtures.json')


@task
def backup(forced=False):
    '''Dumps remote database and stores it in backups folder.'''
    remote_path = '{}/backups/{}'.format(env.komoo_project_folder, DBFILE())
    if env.exists(remote_path):
        if not forced:
            return remote_path
    env.run('pg_dump -U {} --no-privileges --no-owner {} > {}'.format(
        env.komoo_dbuser,
        env.komoo_dbname,
        remote_path))
    return remote_path


@task
def loaddata(file_):
    '''Loads data from json file.'''
    env.run('psql -U {} {} < {}'.format(
        env.komoo_dbuser, env.komoo_dbname, file_))


def DBFILE():
    return 'backupdb_{}_{}.sql'.format(
            env.komoo_env, datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))


@task
def getcopy():
    '''Backs up remote database and transfers a copy of it locally.'''
    local_path = DBFILE()
    if os.path.exists(local_path):
        if not confirm('Backup exists locally at {}. Do you want to '
                       'overwrite it?'.format(local_path)):
            return local_path
    remote_path = backup()
    env.getfile(remote_path, local_path)
    return local_path


@task
def migrate_database(script):
    '''Dumps database to a file, runs migration script and loads it back.'''
    input_file = backup()
    output_file = input_file + ' (migrated)'
    env.run('python {script} {inp} {out}'.format(script=script, inp=input_file,
            out=output_file))
    loaddata(output_file)
