# -*- coding: utf8 -*-
from __future__ import unicode_literals

from authentication.models import User
from apps.organization.models import Organization
from resources.models import Resource

from .base import Interpreter


class OrganizationInterpreter(Interpreter):
    '''
        A model of this worksheet is in:
        https://docs.google.com/spreadsheet/ccc?key=
    '''
    header_rows = 2
    worksheet_name = 'organization'
    
    def a_better_row_dict(self, row_dict):
        '''Reorganize a row_dict to something better.'''
        rd = row_dict
        d = {}

        # Controle
        d['id'] = rd['Controle']['ID']
        d['type'] = {
            'organização': Organization,
            'recurso': Resource,
        }[rd['Controle']['Tipo'].lower()]
        d['creator'] = rd['Controle']['Nome do mapeador']
        d['import'] = rd['Controle']['Importar'].lower() == 'sim'

        # Nome
        d['name'] = '{} - {}'.format(rd['Nome']['Sigla'],
                                     rd['Nome']['Nome da organização'])

        return d

    def validate_row_dict(self, better_row_dict):
        d = better_row_dict
        
        o = d['type'].from_dict(d)
        if not o.is_valid():
            e = o.errors
        w = {}

        # Nome
        # TODO: inexact title search
        q = d['type'].objects.filter(name=d['name'])
        if q.exists():
            w['duplicates'] = []
            for obj in q:
                w['duplicates'].append(obj)

        return {'object': o, 'warnings': w, 'errors': e}
