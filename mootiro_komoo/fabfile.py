#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.api import *

#env.hosts = ['me@example.com:22']

django_settings = {
    'dev' : '--settings=settings.development',
    'stage' : '--settings=settings.staging',
    'prod' : '--settings=settings.production'
}
env = 'dev'

def dev():
    """Set environment to development"""
    global env
    env= 'dev'


def test():
    """Set environment to test"""
    global env
    env = 'test'

def prod():
    """Set environment to production"""
    global env
    env = 'prod'

def run():
    """Runs django's development server"""
    local('python manage.py runserver 8001 {}'.format(django_settings[env]))

def syncdb():
    """Runs syncdb (with no input flag)"""
    local('python manage.py syncdb --noinput {}'.format(django_settings[env]))

def recreate_db():
    """Drops komoo database, recreates it with postgis template and runs syncdb
    """
    print "Recreating database 'komoo'"
    local('dropdb mootiro_komoo && createdb -T template_postgis mootiro_komoo')
    syncdb()

def shell():
    """Launches Django interactive shell"""
    local('python manage.py shell {}'.format(django_settings[env]))


def load_fixtures():
    """Loads all fixtures into database"""
    local('python manage.py loaddata apps/need/initial_data.json {}' \
            .format(django_settings[env]))

def help():
    """Fabfile documentation"""
    local('python -c "import fabfile; help(fabfile)"')
