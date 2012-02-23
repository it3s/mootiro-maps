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
    """build environment: pip install everything + patch django for postgis encoding problem on postgres 9.1 """
    local("pip install -r settings/requirements.txt")
    local("patch -p0 `which python | sed -e 's/bin\/python$/lib\/python2.7\/site-packages\/django\/contrib\/gis\/db\/backends\/postgis\/adapter.py/'` ../docs/postgis-adapter-2.patch")


def run():
    """Runs django's development server"""
    local('python manage.py runserver 8001 {}'.format(django_settings[env]))


def syncdb(create_superuser=""):
    """Runs syncdb (with no input flag by default)"""
    noinput = "" if create_superuser else "--noinput"
    local('python manage.py syncdb {} {}'.format(noinput, django_settings[env]))
    system_fixtures()


def recreate_db():
    """Drops komoo database, recreates it with postgis template and runs syncdb
    """
    print "Recreating database 'komoo'"
    local('dropdb mootiro_komoo && createdb -T template_postgis mootiro_komoo')


def shell():
    """Launches Django interactive shell"""
    local('python manage.py shell {}'.format(django_settings[env]))


def system_fixtures():
    """Load fixtures that populates the db with system info"""
    local('python manage.py loaddata apps/need/initial_data.json {}' \
            .format(django_settings[env]))


def test_fixtures():
    """Loads all fixtures into database"""
    local('python manage.py loaddata test_data.json {}' \
            .format(django_settings[env]))


def help():
    """Fabfile documentation"""
    local('python -c "import fabfile; help(fabfile)"')
