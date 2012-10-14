# -*- coding: utf-8 -*-
'''
This module implements django views that interacts with facebook OAuth2
authentication provider.

In addition for this to work, one's should add django urls that serves the
views below.

Reference:
    https://developers.facebook.com/docs/authentication/server-side/
'''
from __future__ import unicode_literals
import requests
import simplejson

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from annoying.decorators import render_to

from main.utils import randstr
from authentication.utils import login as auth_login

from .models import PROVIDERS
from .utils import encode_querystring, decode_querystring
from .utils import get_or_create_user_by_credentials


def login_facebook(request):

    # Step 1: Getting authorization from the user
    csrf_token = randstr(10)
    redirect_uri = request.build_absolute_uri(reverse('facebook_authorized'))
    params = {
        'client_id': settings.FACEBOOK_APP_ID,  # app id from provider
        'redirect_uri': redirect_uri,  # where the user will be redirected to
        'scope': 'email',              # comma separated list of permissions
        'state': csrf_token,           # unique string to prevent CSRF
    }
    request.session['state'] = csrf_token
    request.session['next'] = request.GET.get('next', reverse('root'))
    url = 'https://www.facebook.com/dialog/oauth'
    url += '?' + encode_querystring(params)
    return redirect(url)


@render_to('authentication/login.html')
def facebook_authorized(request):
    csrf_token = request.GET.get('state', None)
    if not csrf_token or csrf_token != request.session['state']:
        return HttpResponse(status=403)  # csrf attack! get that bastard!

    error = request.GET.get('error', None)
    if error:
        error_description = request.GET.get('error_description', None)
        return dict(login_error='facebook', error_msg=error_description)

    # Step 2: Exchange the authorization code for an access_token
    redirect_uri = request.build_absolute_uri(reverse('facebook_authorized'))
    params = {
        'client_id': settings.FACEBOOK_APP_ID,
        'client_secret': settings.FACEBOOK_APP_SECRET,
        'code': request.GET.get('code'),  # code to exchange for access_token
        'redirect_uri': redirect_uri,     # must be the same as in step1
    }
    url = 'https://graph.facebook.com/oauth/access_token'
    url += '?' + encode_querystring(params)
    access_data = decode_querystring(requests.get(url).text)

    # Step 3: Accessing the API
    params = {
        'fields': 'email,name',
        'access_token': access_data['access_token'],
    }
    url = 'https://graph.facebook.com/me'
    url += '?' + encode_querystring(params)
    data = simplejson.loads(requests.get(url).text)

    user, created = get_or_create_user_by_credentials(data['email'],
                                    PROVIDERS['facebook'], access_data)
    if created:
        user.name = data['name']
        user.save()

    auth_login(request, user)

    return redirect(request.session['next'] or reverse('root'))
