# -*- coding: utf-8 -*-
'''

Reference:
    https://developers.google.com/accounts/docs/OAuth2WebServer#offline
    https://developers.google.com/api-client-library/python/reference/pydoc
    https://developers.google.com/apis-explorer/
'''
from __future__ import unicode_literals

import feedparser
from gdata.spreadsheets.client import SpreadsheetsClient

from annoying.decorators import render_to
from .token import google_drive_service, google_spreadsheets_service
from .token import get_access_token, get_tok


@render_to('importsheet/poc.html')
def poc(request):

    key = '0Ahdnyvg2LXX-dDFITkdXd0hBNFBDczA4RFV2dVBVM0E'
    gd = google_drive_service(request)
    # gs = google_spreadsheets_service(request)
    gs = SpreadsheetsClient()

    # Copiar um documento
    if request.GET['action'] == 'copy':
        data = gd.files().copy(fileId=key, body=dict(title="Copia")).execute()
    
    # Baixar uma worksheet especifica
    if request.GET['action'] == 'worksheet':
        data = gs.get_list_feed(key, 'od6', auth_token=get_tok())
        data = feedparser.parse(str(data))
        entries = []
        for entry in data['entries']:
            entries.append({k[4:]:v for k, v in entry.items() if k.startswith('ns4')})
        data = entries


    print get_access_token()

    return dict(action=request.GET['action'], data=data)
