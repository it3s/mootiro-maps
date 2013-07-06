#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.api import local

from .base import logging, django_settings, env_, setup_django


def sync_db(create_superuser=""):
    """Runs syncdb (with no input flag by default)"""
    noinput = "" if create_superuser else "--noinput"
    local('python mootiro_maps/manage.py syncdb {} {}'
          .format(noinput, django_settings[env_]))


def syncdb(create_superuser=""):
    sync_db(create_superuser)


def create_db():
    """Create komoo database with postgis template."""
    setup_django()
    from django.conf import settings
    db_name = settings.DATABASES['default']['NAME']
    logging.info("Creating database '{}'".format(db_name))
    local('createdb -T template_postgis {}'.format(db_name))


def drop_db():
    """Drops komoo database """
    setup_django()
    from django.conf import settings
    db_name = settings.DATABASES['default']['NAME']
    logging.info("Droping database '{}'".format(db_name))
    local('dropdb {}'.format(db_name))


def recreate_db():
    """Drops komoo database and recreates it with postgis template."""
    drop_db()
    create_db()


def sync_all(data_fixtures='fixtures/backupdb.json'):
    """
    restart app and database from scratch.
    It: drops the DB, recreates it, syncdb, load_fixtures and call
    initial_revisions, also makes coffee and hugs you. :)
    """
    recreate_db()
    syncdb()
    fix_contenttypes()
    if data_fixtures == "test":
        load_fixtures(data_fixtures)
    else:
        loaddata(data_fixtures)
    loaddata('fixtures/contenttypes_fixtures.json')


def dumpdata():
    """Dump DB data, for backup purposes """
    import datetime
    local('python mootiro_maps/manage.py dumpdata {} > backupdb_{}.json'
          .format(django_settings[env_],
                  datetime.datetime.now().strftime('%Y_%m_%d')))


def load_fixtures(type_='system'):
    """
    load fixtures (system and test).
    usage:
      fab load_fixtures  ->  loads all files which name ends with
                             '_fixtures.json' inside the fixtures folder
                             (except for 'test_fixtures.json')
      fab load_fixtures:test  -> load only the fixtures/test_fixtures.json file
    """
    import os
    if type_ == 'test':
        fixtures = ""
        folder = 'fixtures/test'
        for fixture in os.listdir(folder):
            if (fixture.endswith('.json') and
                    fixture != 'contenttypes_fixtures.json'):

                fixtures += "{}/{} ".format(folder, fixture)
        local('python mootiro_maps/manage.py loaddata {} {}'.format(
            fixtures, django_settings[env_]))
    else:
        for fixture in os.listdir('fixtures'):
            if fixture.endswith('_fixtures.json'):
                local('python mootiro_maps/manage.py loaddata fixtures/{} {}'
                      .format(fixture, django_settings[env_]))


def loaddata(fixture_file=None):
    """
    load a single fixture file
    usage:
        fab loaddata:fixture_file_path -> loads the given fixture file to db
    """
    if fixture_file:
        local('python mootiro_maps/manage.py loaddata {} {}'.format(
            fixture_file, django_settings[env_]))
    else:
        logging.info("""
        Please provide a fixture file
        usage:
          fab loaddata:fixture_file_path -> loads the given fixture file to db
        """)


def fix_contenttypes():
    """ remove auto added contenttypes from django for loading data """
    setup_django()
    from django.contrib.contenttypes.models import ContentType

    logging.info('cleaning contenttypes ... ')
    ContentType.objects.all().delete()
    loaddata('fixtures/contenttypes_fixtures.json')
