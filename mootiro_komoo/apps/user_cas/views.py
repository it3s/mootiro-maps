#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import requests

from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from annoying.decorators import render_to, ajax_request

from signatures.models import Signature
from django_cas.views import _logout_url as cas_logout_url


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
    next_page = request.GET.get('next', '/')
    auth_logout(request)
    requests.get(cas_logout_url(request, next_page))
    # request.get("https://www.facebook.com/logout.php?next=YOUR_REDIRECT_URL&access_token=USER_ACCESS_TOKEN")
    return redirect(next_page)


@render_to('user_cas/login_test.html')
def test_login(request):
    logger.debug('\nUSER:\n{}\n{}'.format(dir(request.user), request.user.username))
    return {}


@render_to('user_cas/profile.html')
@login_required
def profile(request):
    logger.debug('accessing user_cas > profile')
    signatures = Signature.objects.filter(user=request.user)
    return {'signatures': signatures}


@login_required
@ajax_request
def profile_update(request):
    logger.debug('accessing user_cas > profile_update')
    logger.debug('POST: {}'.format(request.POST))

    user = request.user
    username = request.POST.get('username', '')
    signatures = request.POST.get('signatures', [])

    success = True
    errors = {}

    # validations
    if not username:
        success = False
        errors['username'] = _('You must provide a username')
    if User.objects.filter(username=username).exclude(pk=user.id).count():
        success = False
        errors['username'] = _('This username already exists')

    if not errors and success:
        # save username
        user.username = username
        user.save()

        # update signatures
        if signatures:
            signatures = map(int, signatures)
            for signature in Signature.objects.filter(user=user):
                if not signature.id in signatures:
                    signature.delete()
        return {'success': 'true', 'redirect': reverse('user_profile')}

    return {'success': 'false', 'errors': errors}
