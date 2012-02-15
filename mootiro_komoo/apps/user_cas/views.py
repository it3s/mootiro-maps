#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''This module is unfinished and not being used. We are instead using
django-cas with some customization done on kommo.__init__.py.
'''
from __future__ import unicode_literals  # unicode by default
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.conf import settings
from annoying.decorators import render_to


def login(request):
    '''When the user clicks "login" on Mootiro Bar, this view runs.
    It redirects the user to CAS.
    '''
    host_port = request.environ['HTTP_HOST']
    return redirect(settings.CAS_SERVER_URL + \
        '?service=http://{}/user/after_login'.format(host_port))


def after_login(request):
    '''When the user authenticates against CAS, he gets redirected here.
    We check the ticket agains the CAS server, then
    log him into this application and redirect to / .
    '''
    # Check the ticket against CAS
    # Log the user in
    # Redirect to /


def logout(request):
    print('logout')
