#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.api import local

from .base import django_settings, env_

def makemessages(lang='pt_BR'):
    """create translations messages file"""
    local('python mootiro_maps/manage.py makemessages -l {} {}'.format(
        lang, django_settings[env_]))
    local('python mootiro_maps/manage.py makemessages -d djangojs -l {} {}'
          .format(lang, django_settings[env_]))


def compilemessages():
    """
    compile messages file
    """
    local('python mootiro_maps/manage.py compilemessages {}'
          .format(django_settings[env_]))
