#! /usr/bin/env python
# -*- coding:utf-8 -*-
import os

from fabric.state import env
from fabric.api import task, warn


@task(aliases=['directory', 'path'])
def dir():
    if not env.exists(env.komoo_project_folder):
        warn('Project path not found: {}'.format(env.komoo_project_folder))
        return False
    return True


@task(alias='repository')
def repo():
    if not dir() or not env.exists(os.path.join(env.komoo_project_folder,
                                                '.git')):
        warn('Repository not found.')
        return False
    return True


@task
def virtualenv():
    if not env.exists('~/.virtualenvs/{}'.format(env.komoo_virtualenv)):
        warn('Virtualenv not found.')
        return False
    return True


