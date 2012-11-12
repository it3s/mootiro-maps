# -*- coding: utf8 -*-
from __future__ import unicode_literals

from .base import Interpreter


class OrganizationInterpreter(Interpreter):
    '''
        A model of this worksheet is in:
        https://docs.google.com/spreadsheet/ccc?key=
    '''
    header_rows = 2
    worksheet_name = 'organization'
    
    def validate_row(self, row_dict):
        raise NotImplementedError()

    def arrange_row_dict(self, row_dict):
        return row_dict
