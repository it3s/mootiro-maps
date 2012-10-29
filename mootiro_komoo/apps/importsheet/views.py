# -*- coding: utf-8 -*-
'''

Reference:
    https://developers.google.com/api-client-library/python/reference/pydoc
    https://developers.google.com/apis-explorer/
'''
from __future__ import unicode_literals

from apiclient.discovery import build

from annoying.decorators import render_to


@render_to('importsheet/poc.html')
def poc(request):
    return dict()



import httplib2
from oauth2client.client import OAuth2WebServerFlow

# Run through the OAuth flow and retrieve credentials
flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE)
authorize_url = flow.step1_get_authorize_url()
print 'Go to the following link in your browser: ' + authorize_url
code = raw_input('Enter verification code: ').strip()
credentials = flow.step2_exchange(code)

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)
drive_service.files().copy(fileId=origin_file_id, body=copied_file).execute()
