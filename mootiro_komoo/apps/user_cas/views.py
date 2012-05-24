#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''This module is unfinished and not being used. We are instead using
django-cas with some customization done on kommo.__init__.py.
'''
from __future__ import unicode_literals  # unicode by default
import logging

from django.shortcuts import redirect
from django.conf import settings

from annoying.decorators import render_to


logger = logging.getLogger(__name__)


def login(request):
    '''When the user clicks "login" on Mootiro Bar, this view runs.
    It redirects the user to CAS.
    '''
    logger.debug('accessing user_cas > login')
    host_port = request.environ['HTTP_HOST']
    return redirect(settings.CAS_SERVER_URL + \
        '?service=http://{}/user/after_login'.format(host_port))


def after_login(request):
    '''When the user authenticates against CAS, he gets redirected here.
    We check the ticket agains the CAS server, then
    log him into this application and redirect to / .
    '''
    logger.debug('accessing user_cas > after_login')
    # Check the ticket against CAS
    # Log the user in
    # Redirect to /


def logout(request):
    logger.debug('accessing user_cas > logout')


@render_to('user_cas/login_test.html')
def test_login(request):
    logger.debug('\nUSER:\n{}\n{}'.format(dir(request.user), request.user.username))
    return {}


@render_to('user_cas/profile.html')
def profile(request):
    logger.debug('accessing user_cas > profile')
    return {}
