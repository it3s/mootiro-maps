# -*- coding: utf-8 -*-
'''

Reference:
    https://developers.google.com/accounts/docs/OAuth2WebServer#offline
    https://developers.google.com/api-client-library/python/reference/pydoc
    https://developers.google.com/apis-explorer/
'''
from __future__ import unicode_literals

from annoying.decorators import render_to
from .token import google_drive_service, google_spreadsheets_service


@render_to('importsheet/poc.html')
def poc(request):

    k = '0Ahdnyvg2LXX-dDFITkdXd0hBNFBDczA4RFV2dVBVM0E'
    gd = google_drive_service(request)
    gs = google_spreadsheets_service(request)

    # Copiar um documento
    if request.GET['action'] == 'copy':
        d = gd.files().copy(fileId=k, body=dict(title="Copia")).execute()
    
    # Baixar uma worksheet especifica
    if request.GET['action'] == 'worksheet':
        # gs =  
        pass

    return dict()
