#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.state import env
from fabric.api import task

from .base import virtualenv


@task(alias='make')
def makemessages(lang='pt_BR'):
    """create translations messages file"""
    with virtualenv(), env.cd('mootiro_maps'):
        env.run('python manage.py makemessages -l {} {}'.format(
            lang, env.komoo_django_settings))
        env.run('python manage.py makemessages'
                ' -d djangojs -l {} {}'.format(
                    lang, env.komoo_django_settings))


@task(alias='compile')
def compilemessages():
    """
    compile messages file
    """
    with virtualenv(), env.cd('mootiro_maps'):
        env.run('python manage.py compilemessages {}'
                .format(env.komoo_django_settings))
