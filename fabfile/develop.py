#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.state import env
from fabric.api import task

from .base import virtualenv

@task
def work():
    """Start watchers"""
    # compilers
    with virtualenv():
        env.run('./scripts/coffee_compiler.js &')
        env.run('sass --watch ./ &')

    # test runners go here!


@task
def update_reform():
    """ update reForm fro, repo """
    with virtualenv():
        env.run('wget -O static/lib/reForm.js '
              'https://raw.github.com/it3s/reform/master/src/reForm.js')
