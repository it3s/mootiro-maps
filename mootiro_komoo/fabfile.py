#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.api import *

#env.hosts = ['me@example.com:22']

django_settings = {
    'dev': '--settings=settings.development',
    'stage': '--settings=settings.staging',
    'prod': '--settings=settings.production'
}
env = 'dev'


def dev():
    """Set environment to development"""
    global env
    env = 'dev'


def test():
    """Set environment to test"""
    global env
    env = 'test'


def prod():
    """Set environment to production"""
    global env
    env = 'prod'


def build_environment():
    """
    build environment: pip install everything + patch django for postgis
    encoding problem on postgres 9.1
    """
    local("pip install -r settings/requirements.txt")
    local("patch -p0 `which python | "
        "sed -e 's/bin\/python$/lib\/python2.7\/site-packages\/django\/contrib\/gis\/db\/backends\/postgis\/adapter.py/'` "
        "../docs/postgis-adapter-2.patch")


def run():
    """Runs django's development server"""
    local('python manage.py runserver 8001 {}'.format(django_settings[env]))


def js_urls():
    """Creates a javascript file containing urls"""
    local('python manage.py js_urls {}'.format(django_settings[env]))


def syncdb(create_superuser=""):
    """Runs syncdb (with no input flag by default)"""
    noinput = "" if create_superuser else "--noinput"
    local('python manage.py syncdb {} {}'.format(noinput, django_settings[env]))
    load_fixtures()


def recreate_db():
    """Drops komoo database, recreates it with postgis template and runs syncdb
    """
    print "Recreating database 'komoo'"
    local('dropdb mootiro_komoo && createdb -T template_postgis mootiro_komoo')


def shell():
    """Launches Django interactive shell"""
    local('python manage.py shell {}'.format(django_settings[env]))


def load_fixtures(type_='system'):
    """
    load fixtures (system and test).
    usage:
        fab load_fixtures  ->  loads all files which name ends with '_fixtures.json'
            inside the fixtures folder (except for 'test_fixtures.json')
        fab load_fixtures:test  -> load only the fixtures/test_fixtures.json file
    """
    if type_ == 'test':
        local('python manage.py loaddata fixtures/test_fixtures.json {}'.format(
                django_settings[env]))
    else:
        import os
        for fixture in os.listdir('fixtures'):
            if fixture.endswith('_fixtures.json') and fixture != 'test_fixtures.json':
                local('python manage.py loaddata fixtures/{} {}'.format(
                    fixture, django_settings[env]))


def initial_revisions():
    """
    load initial revisions for django-revisions module
    should run only once when installed/or when loaded a new app/model
    """
    local('python manage.py createinitialrevisions {}'.format(django_settings[env]))


def sync_all():
    """
    restart app and database from scratch.
    It: drops the DB, recreates it, syncdb, load_fixtures and call initial_revisions,
    also makes coffee and give you a hug
    """
    recreate_db()
    syncdb()
    load_fixtures('test')
    initial_revisions()


def help():
    """Fabfile documentation"""
    local('python -c "import fabfile; help(fabfile)"')
