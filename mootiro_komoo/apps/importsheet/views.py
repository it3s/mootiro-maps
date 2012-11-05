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

    skey = '0Ahdnyvg2LXX-dDFITkdXd0hBNFBDczA4RFV2dVBVM0E'
    wkey = 'od6'
    gd = google_drive_service(request)
    # gs = google_spreadsheets_service(request)
    gs = SpreadsheetsClient()
    data = None

    # Copiar um documento
    if request.GET['action'] == 'copy':
        data = gd.files().copy(fileId=skey, body=dict(title="Copia")).execute()

    if request.GET['action'] == 'new':
        project_folder_template_key = '0Bxdnyvg2LXX-MDdZcmE0aDFnS2c'
        PROJECTS_FOLDER = '0Bxdnyvg2LXX-MDdZcmE0aDFnS2c'

        data = gd.files().insert(
                    body=dict(
                        title="Projeto Novo",
                        parents=[{'id': PROJECTS_FOLDER}],
                        mimeType="application/vnd.google-apps.folder"
                    )
                ).execute()

        gd.files().copy(
            fileId=skey,
            body=dict(parents=[{'id': data['id']}])
        ).execute()

    
    # Baixar uma worksheet especifica
    if request.GET['action'] == 'worksheet':
        data = gs.get_list_feed(skey, wkey, auth_token=get_tok())
        data = feedparser.parse(str(data))
        entries = []
        for entry in data['entries']:
            entries.append({k[4:]:v for k, v in entry.items() if k.startswith('ns4')})
        data = entries

    # Baixar um intervalo de linhas específico
    if request.GET['action'] == 'interval':
        # é preciso usar um feed de células diretamente
        params = {'min-row': '1', 'max-row': '1'}
        data = gs.get_cells(skey, wkey, auth_token=get_tok(), **params)
        h = feedparser.parse(str(data))
        columns = {}
        for e in h['entries']:
            e = e['ns3_cell']
            columns[e['col']] = e['inputvalue']

        params = {'min-row': '2'}
        data = gs.get_cells(skey, wkey, auth_token=get_tok(), **params)
        d = feedparser.parse(str(data))
        rows = {}  # a line number indexed dict of dict objects
        for e in d['entries']:
            e = e['ns3_cell']
            if not e['row'] in rows:
                rows[e['row']] = {}
            obj = rows[e['row']]  # the properly obj dict
            attr = columns[e['col']]
            obj[attr] = e['inputvalue']
        data = rows

    if request.GET['action'] == 'config':
        # pegar o endereço de uma worksheet pelo nome
        # data = cs.get_worksheets(skey, auth_token=tok)
        # d = feedparser.parse(str(data))
        # worksheet_keys = {e['title']:e['id'].split('/')[-1] for e in d['entries']}
        # wkey = worksheet_keys['config']

        # TODO: se for usar essa lib, precisa remover as libs não usadas do
        # arquivo de dependências (requirements.txt)
        import gspread
        gc = gspread.login('it3sdev@gmail.com','weareawesome')
        sh = gc.open_by_key(skey)
        worksheet = sh.worksheet('config')
        worksheet.update_cell(1, 1, 'Bingo!')
        data = "bingo"



    return dict(action=request.GET['action'], data=data)
