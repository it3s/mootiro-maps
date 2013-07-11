#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.api import local, task

from .base import logging, django_settings, env_
from .i18n import compilemessages
from .test import test_js


@task
def collect_js(apps=None):
    """Collect javascript files from apps"""
    import os
    from shutil import copytree, rmtree, ignore_patterns

    ## Get the project base path
    proj_path = os.path.join(os.path.dirname(__file__), '../../mootiro_maps')
    build_path = os.path.join(proj_path, '../.build')

    try:
        logging.info('cleaning build path ... ')
        rmtree(build_path)
    except OSError, e:
        logging.info(e)

    logging.info('copying javascript files ... ')
    from_ = os.path.join(proj_path, 'static', 'js')
    to = build_path
    copytree(from_, to, ignore=ignore_patterns('*.coffee', '*~'))


@task
def build_js():
    """Combine and minify RequireJS modules"""
    import os
    from shutil import copytree, rmtree, ignore_patterns
    collect_js()

    proj_path = os.path.join(os.path.dirname(__file__), '../../mootiro_maps')
    build_path = os.path.join(proj_path, '../.build')
    local('r.js -o app.build.js')
    from_ = os.path.join(build_path, 'min')
    to = os.path.join(proj_path, 'static', 'js.build')
    try:
        rmtree(to)
    except OSError:
        pass
    logging.info('copying compiled javascripts to {}'.format(to))
    copytree(from_, to, ignore=ignore_patterns('*.coffee', '*~'))

    # Removes the build dir
    rmtree(build_path)

    test_js()


@task
def js_urls():
    """Creates a javascript file containing urls"""
    local('python mootiro_maps/manage.py js_urls {}'.format(
        django_settings[env_]))

    # remove trailing interrogations
    logging.info('removing trailing "?" from urls')
    import os
    s = ''
    with open(
            os.path.abspath(
            './mootiro_maps/static/lib/django-js-utils/dutils.conf.urls.js'),
            'r') as f:
        s = f.read()
        s = s.replace('?', '')
    with open(
            os.path.abspath(
            './mootiro_maps/static/lib/django-js-utils/dutils.conf.urls.js'),
            'w') as f:
        f.write(s)


@task
def compile_coffee():
    """Compiles coffeescript to javascript"""
    local('./scripts/coffee_compiler.js --all')


@task
def compile_sass():
    """Compiles sass to css"""
    local('sass --update ./')


@task(default=True)
def build():
    """Build step"""
    compilemessages()
    js_urls()
    compile_coffee()
    compile_sass()
    build_js()
