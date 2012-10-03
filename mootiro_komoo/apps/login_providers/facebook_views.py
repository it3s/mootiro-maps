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

from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from annoying.decorators import render_to

from main.utils import randstr

# TODO: move these configurations to settings/common.py
FACEBOOK_APP_ID = '186391648162058'
FACEBOOK_APP_SECRET = 'd6855cacdb51225519e8aa941cf7cfee'


def make_querystring(base_url, params):
    s = base_url
    if params:
        s += '?' + '&'.join(['%s=%s' % (k, v) for k, v in params.items()])
    return s


def parse_querystring(s):
    return {p.split('=')[0]:p.split('=')[1] for p in s.split('&')}


def login_facebook(request):
    base_url = 'https://www.facebook.com/dialog/oauth'
    csrf_token = randstr(10)
    params = {
        # client_id: app id from provider.
        # redirect_uri: where the user will be redirected to.
        # scope: comma separated list of requested permissions.
        # state: some arbitrary but unique string. Used to prevent from CSRF.
        'client_id': FACEBOOK_APP_ID,
        'redirect_uri': request.build_absolute_uri(reverse('facebook_authorized')),
        'scope': 'email',
        'state': csrf_token,
    }
    request.session['state'] = csrf_token
    url = make_querystring(base_url, params)
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

    base_url = 'https://graph.facebook.com/oauth/access_token'
    params = {
        # client_id: app id from provider.
        # client_secret: app secret from provider.
        # code: code given by provider to exchange for an access_token.
        # redirect_uri: must be the same as the one in step 1.
        'client_id': FACEBOOK_APP_ID,
        'client_secret': FACEBOOK_APP_SECRET,
        'code': request.GET.get('code'),
        'redirect_uri': request.build_absolute_uri(reverse('facebook_authorized')),
    }
    url = make_querystring(base_url, params)
    data = parse_querystring(requests.get(url).text)
    print "DATA = = = = = =", data
    access_token = data['access_token']

#     href = Href('https://graph.facebook.com/')
#     href = href('me', fields='email,name', access_token=access_token)
#     resp = requests.get(href)
#     data = simplejson.loads(resp.content)

#     # TODO: create user using name and email
#     # TODO: persist access_token (or auth_code?) and expiration in DB

#     user = User()
#     # user.email = data['email']
#     session['email'] = data['email']
#     login_user(user)

#     return redirect(url_for('user.secret'))

