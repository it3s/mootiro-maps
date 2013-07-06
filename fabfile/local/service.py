#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.api import local

from .base import django_settings, env_, setup_django, kill_tasks


def configure_elasticsearch():
    """ configure elasticsearch from scratch """
    run_elasticsearch(bg='true')
    local('sleep 10s')
    setup_django()
    from search.utils import reset_index, create_mapping
    reset_index()
    create_mapping()
    kill_tasks('elasticsearch')


def run_elasticsearch(bg='false'):
    """
    run elastic search
    usage:
        fab run_elasticsearch  #runs on foreground
        fab run_elasticsearch:bg=true  #runs on background
    """
    background = '&' if bg == 'true' else ''
    local('./lib/elasticsearch/bin/elasticsearch -f {}'.format(background))


def run_datalog():
    """ Runs Datalog's Flask/MongoDB web server """
    local('python lib/datalog/app.py &')


def run_celery():
    """runs celery task queue"""
    local('python mootiro_maps/manage.py celeryd -B --loglevel=info {} &'
          .format(django_settings[env_]))
