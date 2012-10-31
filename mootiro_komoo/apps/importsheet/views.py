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
from .token import get_access_token, get_tok



@render_to('importsheet/poc.html')
def poc(request):

    key = '0Ahdnyvg2LXX-dDFITkdXd0hBNFBDczA4RFV2dVBVM0E'
    gd = google_drive_service(request)
    # gs = google_spreadsheets_service(request)

    # Copiar um documento
    if request.GET['action'] == 'copy':
        data = gd.files().copy(fileId=key, body=dict(title="Copia")).execute()
    
    # Baixar uma worksheet especifica
    if request.GET['action'] == 'worksheet':

        from gdata.spreadsheets.client import SpreadsheetsClient
        cs = SpreadsheetsClient()
        data = cs.get_list_feed(key, 'od6', auth_token=get_tok())
        import pdb; pdb.set_trace()
        print "\n\n"
        print type(data)
        print "\n\n"
        # data = cs.get_worksheets(key, auth_token=get_tok())
        # data = cs.get_list_feed(key, 'od6', auth_token=get_tok())

        # from gdata.spreadsheet.service import SpreadsheetsService
        # serv = SpreadsheetsService(email='it3sdev@gmail.com', password='weareawesome')
        # data = serv.GetWorksheetsFeed(key, 'od6')

    print get_access_token()

    return dict(action=request.GET['action'], data=data)
