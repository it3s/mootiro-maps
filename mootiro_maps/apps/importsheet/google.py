# -*- coding: utf-8 -*-
'''
These views exists as a easy way to get a refresh code for a given google 
account. Once you get the refresh code store it securely!
'''
from __future__ import unicode_literals
import requests
import simplejson as json
import httplib2

from django.conf import settings
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

# Google API
from apiclient.discovery import build
from oauth2client.client import AccessTokenCredentials

from annoying.decorators import render_to
from authentication.utils import encode_querystring


def refresh_token(request):
    '''Getting authorization from the user.'''
    redirect_uri = request.build_absolute_uri(
                        reverse('importsheet_refresh_token_authorized'))
    params = {
        'client_id': settings.GOOGLE_APP_ID,
        'redirect_uri': redirect_uri,
        # below a space separated list of permissions
        'scope': 'https://www.googleapis.com/auth/drive '
                 'https://www.googleapis.com/auth/drive.file '
                 'https://spreadsheets.google.com/feeds '
                 'https://www.googleapis.com/auth/fusiontables '
                 'https://www.googleapis.com/auth/fusiontables.readonly',
        'access_type': 'offline',
        'response_type': 'code',
        'approval_prompt': 'force',
    }
    url = 'https://accounts.google.com/o/oauth2/auth'
    url += '?' + encode_querystring(params)
    return redirect(url)


# TODO: remove this!
@render_to('importsheet/refresh_token.html')
def refresh_token_authorized(request):
    '''Exchange the authorization code for an refresh token and displays it.'''
    error = request.GET.get('error', None)
    if error:
        error_description = request.GET.get('error_description', None)
        return dict(error=error_description)

    redirect_uri = request.build_absolute_uri(
                        reverse('importsheet_refresh_token_authorized'))
    params = {
        'client_id': settings.GOOGLE_APP_ID,
        'client_secret': settings.GOOGLE_APP_SECRET,
        'code': request.GET.get('code'),
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }
    url = 'https://accounts.google.com/o/oauth2/token'
    resp = requests.post(url, data=params)
    access_data = json.loads(resp.text)
    refresh_token = access_data['refresh_token']

    print "\n\n"
    print 'REFRESH_TOKEN:', refresh_token
    print "\n\n"

    return dict()


def get_access_token():
    # TODO: only refresh the token if expired
    params = {
        'client_id': settings.GOOGLE_APP_ID,
        'client_secret': settings.GOOGLE_APP_SECRET,
        'refresh_token': settings.IMPORTSHEET_REFRESH_TOKEN,
        'grant_type': 'refresh_token',
    }
    url = 'https://accounts.google.com/o/oauth2/token'
    resp = requests.post(url, data=params)
    data = json.loads(resp.text)
    access_token = data['access_token']
    return access_token


def authorized_http():
    user_agent = 'Python-urllib/2.7'  # it could be anything
    credentials = AccessTokenCredentials(get_access_token(), user_agent)
    http = httplib2.Http()
    http = credentials.authorize(http)
    return http


def google_drive_service():
    '''Build and return a google drive service via OAuth2 to interact with.'''
    http = authorized_http()
    service = build('drive', 'v2', http)
    return service


def google_fusion_tables_service():
    '''Build and return a google fusion tables service via OAuth2 to interact
    with.'''
    http = authorized_http()
    service = build('fusiontables', 'v1', http)
    return service    
