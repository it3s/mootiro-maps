# -*- coding: utf-8 -*-
'''
This is script is an interactive way of exploring google spreadsheet API XMLs.
  To use it, do:

    fab shell
    run apps/importsheet/test

  ... inspect your variables. Good Luck! ...
'''
import feedparser

from gdata.spreadsheets.client import SpreadsheetsClient
from gdata.gauth import AuthSubToken

from importsheet.token import get_access_token


access_token = get_access_token()
tok = AuthSubToken(token_string=access_token)
skey = '0Ahdnyvg2LXX-dDFITkdXd0hBNFBDczA4RFV2dVBVM0E'
wkey = 'od6'
cs = SpreadsheetsClient()

params = {'min-row': '1', 'max-row': '1'}
data = cs.get_cells(skey, wkey, auth_token=tok, **params)
h = feedparser.parse(str(data))

params = {'min-row': '2'}
data = cs.get_cells(skey, wkey, auth_token=tok, **params)
d = feedparser.parse(str(data))

# ... d is a browseable dict ... Good Luck!
