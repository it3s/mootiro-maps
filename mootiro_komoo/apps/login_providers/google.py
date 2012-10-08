# -*- coding: utf-8 -*-
'''
This module implements django views that interacts with google OAuth2
authentication provider.

In addition for this to work, one's should add django urls that serves the
views below.

Reference:
    Step 1: Getting authorization from the user
    https://developers.google.com/accounts/docs/OAuth2Login

    Step 2: Exchange the authorization code for an access_token
    https://developers.google.com/accounts/docs/OAuth2WebServer

    Step 3: Accessing the API
'''
from __future__ import unicode_literals
import requests
import simplejson

from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from annoying.decorators import render_to

from main.utils import randstr
from komoo_user.utils import login as auth_login
from .models import PROVIDERS
from .utils import encode_querystring
from .utils import get_or_create_user_by_credentials

# TODO: move these configurations to settings/common.py
GOOGLE_APP_ID = '806210666216.apps.googleusercontent.com'
GOOGLE_APP_SECRET = 'wWFaxUXs3C7atzHThA-YD8T3'


def login_google(request):

    # Step 1: Getting authorization from the user
    csrf_token = randstr(10)
    redirect_uri = request.build_absolute_uri(reverse('google_authorized'))
    params = {
        'client_id': GOOGLE_APP_ID,    # app id from provider
        'redirect_uri': redirect_uri,  # where the user will be redirected to
        'scope': 'https://www.googleapis.com/auth/userinfo.profile '  # space separated
                 'https://www.googleapis.com/auth/userinfo.email',    # list of permissions
        'state': csrf_token,           # unique string to prevent CSRF
        'response_type': 'code',       # 'code' or 'token', depends on the application type.
    }
    request.session['state'] = csrf_token
    request.session['next'] = request.GET.get('next', reverse('root'))
    url = 'https://accounts.google.com/o/oauth2/auth'
    url += '?' + encode_querystring(params)
    return redirect(url)


# @render_to('komoo_user/login.html')
def google_authorized(request):
    csrf_token = request.GET.get('state', None)
    if not csrf_token or csrf_token != request.session['state']:
        return HttpResponse(status=403)  # csrf attack! get that bastard!

    error = request.GET.get('error', None)
    if error:
        error_description = request.GET.get('error_description', None)
        return dict(login_error='google', error_msg=error_description)

    # Step 2: Exchange the authorization code for an access_token
    redirect_uri = request.build_absolute_uri(reverse('google_authorized'))
    params = {
        'client_id': GOOGLE_APP_ID,          # app id from provider
        'client_secret': GOOGLE_APP_SECRET,  # app secret from provider
        'code': request.GET.get('code'),     # code to exchange for an access_token
        'redirect_uri': redirect_uri,        # must be the same as the one in step 1
        'grant_type': 'authorization_code',  # just to fulfill the OAuth2 spec
    }
    url = 'https://accounts.google.com/o/oauth2/token'
    resp = requests.post(url, data=params)   # google requires POST, not GET
    access_data = simplejson.loads(resp.text)
    access_token = access_data['access_token']

    # Step 3: Accessing the API
    params = {
        # 'scope': 'https://www.googleapis.com/auth/userinfo.email',  # fields requested
        'access_token': access_data['access_token'],  # the so wanted access token
    }
    url = 'https://www.googleapis.com/oauth2/v1/userinfo/'
    url += '?' + encode_querystring(params)
    data = simplejson.loads(requests.get(url).text)

    user, created = get_or_create_user_by_credentials(data['email'],
                            PROVIDERS['google'], access_data=access_data)

    if created:
        user.name = data['name']
        user.save()

    auth_login(request, user)

    return redirect(request.session['next'] or reverse('root'))
