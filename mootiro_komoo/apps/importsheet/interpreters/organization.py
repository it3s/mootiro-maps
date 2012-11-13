# -*- coding: utf8 -*-
from __future__ import unicode_literals

from authentication import User
from organization.models import Organization
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
        '''
        Receives a row_dict and returns 3 dicts mimetizing object attributes
        structure.
        '''
        rd = row_dict
        d = {}

        # Controle
        d['id'] = rd['Controle']['ID']
        d['type'] = rd['Controle']['Tipo']
        d['creator'] = rd['Controle']['Nome do mapeador']
        d['import'] = True if rd['Controle']['Importar'].lower() == 'sim' else False

        # Nome
        d['name'] = '{} - {}'.format(rd['Nome']['Sigla'],
                                     rd['Nome']['Nome da organização'])

        return dict(object=d, warnings=w, errors=e)


    def validate_row_dict(self, row_dict):
        '''
        Receives a row_dict and returns 3 dicts mimetizing object attributes
        structure.
        '''
        o = {}
        w = {}
        e = {}
        pass
