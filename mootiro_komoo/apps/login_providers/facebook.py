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

from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from annoying.decorators import render_to

from main.utils import randstr
from komoo_user.models import KomooUser
from komoo_user.utils import login as auth_login
from .models import ExternalCredentials as Credentials, PROVIDERS
from .utils import encode_querystring, decode_querystring
from .utils import get_or_create_user_by_credentials


# TODO: move these configurations to settings/common.py
FACEBOOK_APP_ID = '186391648162058'
FACEBOOK_APP_SECRET = 'd6855cacdb51225519e8aa941cf7cfee'


def login_facebook(request):
    csrf_token = randstr(10)
    redirect_uri = request.build_absolute_uri(reverse('facebook_authorized'))
    params = {
        'client_id': FACEBOOK_APP_ID,  # app id from provider
        'redirect_uri': redirect_uri,  # where the user will be redirected to
        'scope': 'email',              # comma separated list of permissions
        'state': csrf_token,           # unique string to prevent CSRF
    }
    request.session['state'] = csrf_token
    request.session['next'] = request.GET.get('next', reverse('root'))
    url = 'https://www.facebook.com/dialog/oauth'
    url += '?' + encode_querystring(params)
    return redirect(url)


@render_to('komoo_user/login.html')
def facebook_authorized(request):
    csrf_token = request.GET.get('state', None)
    if not csrf_token or csrf_token != request.session['state']:
        return HttpResponse(status=403)  # csrf attack! get that bastard!

    error = request.GET.get('error', None)
    if error:
        error_description = request.GET.get('error_description', None)
        return dict(login_error='facebook', error_msg=error_description)

    redirect_uri = request.build_absolute_uri(reverse('facebook_authorized'))
    params = {
        'client_id': FACEBOOK_APP_ID,          # app id from provider
        'client_secret': FACEBOOK_APP_SECRET,  # app secret from provider.
        'code': request.GET.get('code'),       # code to exchange for an access_token.
        'redirect_uri': redirect_uri,          # must be the same as the one in step 1.
    }
    url = 'https://graph.facebook.com/oauth/access_token'
    url += '?' + encode_querystring(params)
    access_data = decode_querystring(requests.get(url).text)

    params = {
        'fields': 'email,name',                # fields requested
        'access_token': access_data['access_token'],  # the so wanted access token
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
