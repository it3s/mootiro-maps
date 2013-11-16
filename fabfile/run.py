#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.state import env
from fabric.api import task

from .base import virtualenv


@task(default=True)
def run(port=False):
    """Runs django's development server"""
    celery()
    elasticsearch(bg='true')
    django(port)


@task
def django(port=False):
    if not port:
        port = env.komoo_port
    if 'dev' not in env.komoo_django_settings:
        with virtualenv(), env.cd('mootiro_maps'):
                env.run('python manage.py run_gunicorn --workers=2 '
                    '--bind=127.0.0.1:{} --settings={}'.format(
                        port, env.komoo_django_settings)
                    )
    else:
        with virtualenv(), env.cd('mootiro_maps'):
            env.run('python manage.py runserver {} --settings={}'
                    .format(port, env.komoo_django_settings))


@task
def elasticsearch(bg='false'):
    """
    run elastic search
    usage:
        fab run_elasticsearch  #runs on foreground
        fab run_elasticsearch:bg=true  #runs on background
    """
    background = '&' if bg == 'true' else ''
    with virtualenv():
        env.run('./lib/elasticsearch/bin/elasticsearch -f {}'.format(
            background))


@task
def celery():
    """runs celery task queue"""
    with virtualenv(), env.cd('mootiro_maps'):
        env.run('python manage.py celeryd -B --loglevel=info --settings={} &'
                .format(env.komoo_django_settings))
