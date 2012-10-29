# -*- coding: utf-8 -*-
'''

Reference:
    https://developers.google.com/accounts/docs/OAuth2WebServer#offline
    https://developers.google.com/api-client-library/python/reference/pydoc
    https://developers.google.com/apis-explorer/
'''
from __future__ import unicode_literals
import httplib2

# Google API
from apiclient.discovery import build
from oauth2client.client import AccessTokenCredentials

from annoying.decorators import render_to
from .token import get_access_token


def google_drive_service(request):
    access_token = get_access_token()
    user_agent = request.META['HTTP_USER_AGENT']
    credentials = AccessTokenCredentials(access_token, user_agent)
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build('drive', 'v2', http)
    return service


@render_to('importsheet/poc.html')
def poc(request):

    k = '0Ahdnyvg2LXX-dDFITkdXd0hBNFBDczA4RFV2dVBVM0E'
    service = google_drive_service(request)

    # Copiar um documento
    d = service.files().copy(fileId=k, body=dict(title="Copia")).execute()
    
    # Baixar uma worksheet especifica



    return dict(
        copy=d['id']

    )
