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
gs = SpreadsheetsClient()

skey = '0Ahdnyvg2LXX-dDFITkdXd0hBNFBDczA4RFV2dVBVM0E'
wname = 'config'

data = gs.get_worksheets(skey, auth_token=tok)
d = feedparser.parse(str(data))
worksheet_keys = {e['title']:e['id'].split('/')[-1] for e in d['entries']}
wkey = worksheet_keys[wname]

data = gs.get_cell(skey, wkey, 1, 1, auth_token=tok)
d = feedparser.parse(str(data))

# ... d is a browseable dict ... Good Luck!
