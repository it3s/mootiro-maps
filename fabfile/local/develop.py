#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.api import local


def work():
    """Start watchers"""
    # compilers
    local('./scripts/coffee_compiler.js &')
    local('sass --watch ./ &')

    # test runners go here!


def update_reform():
    """ update reForm fro, repo """
    local('wget -O static/lib/reForm.js '
          'https://raw.github.com/it3s/reform/master/src/reForm.js')
