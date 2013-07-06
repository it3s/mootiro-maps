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

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from main.utils import randstr
from authentication.utils import login as auth_login

from .models import PROVIDERS
from .utils import encode_querystring
from .utils import get_or_create_user_by_credentials
from .utils import connect_or_merge_user_by_credentials


def login_google(request):
    '''Redirect user to google login and authorization page.'''
    # Step 1: Getting authorization from the user
    csrf_token = randstr(10)
    redirect_uri = request.build_absolute_uri(reverse('google_authorized'))
    params = {
        'client_id': settings.GOOGLE_APP_ID,
        'redirect_uri': redirect_uri,  # where the user will be redirected to
        # below a space separated list of permissions
        'scope': 'https://www.googleapis.com/auth/userinfo.profile '
                 'https://www.googleapis.com/auth/userinfo.email',
        'state': csrf_token,        # unique string to prevent CSRF
        'response_type': 'code',    # 'code' or 'token'
                                    # depends on the application type.
    }
    request.session['state'] = csrf_token
    request.session['next'] = request.GET.get('next', reverse('root'))
    url = 'https://accounts.google.com/o/oauth2/auth'
    url += '?' + encode_querystring(params)
    return redirect(url)


def google_authorized(request):
    '''
    Connect google account information to the current logged user or one with
    same email. If no user is matched, creates a new one.
    '''
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
        'client_id': settings.GOOGLE_APP_ID,
        'client_secret': settings.GOOGLE_APP_SECRET,
        'code': request.GET.get('code'),     # code to exchange access_token
        'redirect_uri': redirect_uri,        # must be the same as in step 1
        'grant_type': 'authorization_code',  # just to fulfill the OAuth2 spec
    }
    url = 'https://accounts.google.com/o/oauth2/token'
    resp = requests.post(url, data=params)   # google requires POST, not GET
    access_data = simplejson.loads(resp.text)
    access_token = access_data['access_token']

    # Step 3: Accessing the API
    params = {
        # 'scope': 'https://www.googleapis.com/auth/userinfo.email',
        'access_token': access_token,
    }
    url = 'https://www.googleapis.com/oauth2/v1/userinfo/'
    url += '?' + encode_querystring(params)
    data = simplejson.loads(requests.get(url).text)

    if request.user.is_authenticated():
        # if a user is already logged, then just connect social auth account
        connect_or_merge_user_by_credentials(logged_user=request.user,
                        email=data['email'], provider=PROVIDERS['google'])
    else:
        user, created = get_or_create_user_by_credentials(data['email'],
                            PROVIDERS['google'], access_data=access_data)
        if created:
            user.name = data['name']
            user.save()
        auth_login(request, user)

    return redirect(request.session['next'] or reverse('root'))

