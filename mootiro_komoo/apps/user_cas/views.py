#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from annoying.decorators import render_to

from ajaxforms import ajax_form
from forms import FormProfile


logger = logging.getLogger(__name__)


def login(request):
    '''
    When the user clicks "login" on Mootiro Bar, this view runs.
    It redirects the user to CAS.
    '''
    logger.debug('accessing user_cas > login')
    host_port = request.environ['HTTP_HOST']
    return redirect(settings.CAS_SERVER_URL + \
        '?service=http://{}/user/after_login'.format(host_port))


# Never used ??
def after_login(request):
    '''
    When the user authenticates against CAS, he gets redirected here.
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
@login_required
def profile(request):
    logger.debug('accessing user_cas > profile')
    form = FormProfile(instance=request.user)
    return {'form': form}


@login_required
@ajax_form(form_class=FormProfile)
def profile_update(reuqest):
    logger.debug('accessing user_cas > profile_update')

    def on_after_save(request, obj):
        return {'redirect': reverse('user_profile')}

    return {'on_after_save': on_after_save}
