#! /usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.state import env
from fabric.api import *

from .base import logging, virtualenv
from .i18n import compilemessages
from .test import js as test_js


def collect_js(apps=None):
    """Collect javascript files from apps"""
    import os
    from shutil import copytree, rmtree, ignore_patterns

    ## Get the project base path
    proj_path = os.path.join(os.path.dirname(__file__), '../mootiro_maps')
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
def js():
    """Combine and minify RequireJS modules"""

    if (env.is_remote):
        abort('You cannot build js files remotely!\n'
              'This should be done in your local development env.')

    import os
    from shutil import copytree, rmtree, ignore_patterns
    collect_js()

    proj_path = os.path.join(os.path.dirname(__file__), '../mootiro_maps')
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


@task(alias='js_urls')
def urls():
    """Creates a javascript file containing urls"""
    with virtualenv(), env.cd('mootiro_maps'):
        env.run('python manage.py js_urls --settings={}'.format(
            env.komoo_django_settings))

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


@task(alias='coffee')
def compile_coffee():
    """Compiles coffeescript to javascript"""
    env.run('./scripts/coffee_compiler.js --all')


@task(aliases=['sass', 'css'])
def compile_sass():
    """Compiles sass to css"""
    env.run('sass --update ./')


@task(default=True)
def build():
    """Build step"""
    compilemessages()
    urls()
    compile_coffee()
    compile_sass()
    js()
