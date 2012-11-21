# -*- coding: utf8 -*-
from __future__ import unicode_literals

import gspread
from copy import deepcopy
from collections import OrderedDict


class Interpreter(object):
    '''
    Interface class for each **worksheet** type interpreter.


    IMPORTANT CONCEPTS:

      row_dict: a dictionary with information from the worksheet indexed with
        its header lines. (see get_rows_dicts method)

      object_dict: a dictionary constructed based on a row_dict. It has just
        one level and its keys are the objects attributes.
        
      parse_dict: a dictionary with information obtained on row_dict validation
        process. Like: {'object_dict': o, 'errors': e, 'warnings': w}
    

    SUBCLASS TEMPLATE:
        You can use the template below to implement a new worksheet
        interpreter.

    class MyAwesomeInterpreter(Interpreter):
        """
        A model of this worksheet is public available in:
        https://docs.google.com/spreadsheet/ccc?key=
        """
        header_rows = 2  # see get_row_dicts method
        worksheet_name = 'my_worksheet_template_name'

        def row_dict_to_parse_dict(self, row_dict):
            raise NotImplementedError('Subclass responsability')

        def object_dict_to_object(self, row_dict):
            raise NotImplementedError('Subclass responsability')
    '''

    def __init__(self, gspread_worksheet):
        self.worksheet = gspread_worksheet

    def get_row_dicts(self):
        '''
        Receives the number of header rows, and return rows values organized as
        a tree dict of the headers.

        Example:
             ____________________ _______________________________
            |       Place        |          Description          |
            |    Name    | Title | Location | Partner? | History |
            |------------|-------|----------|----------|---------|
            | John Doe   | Mr.   | 5th ave  | Yes      | lorem   |
            | Mary Doe   | Mrs.  | 6th ave  |          | ipsum   |
            | Peter Poe  |       | 7th ave  | Yes      |         |
             ------------ ------- ---------- ---------- ---------
            
            wsi = WorksheetInterpreter(gspread_worksheet)
            wsi.get_rows_dicts() ->
                [
                    {
                        'Place': {
                            'Name': 'John Doe',
                            'Title': 'Mr.'
                        },
                        'Description': {
                            'Location': '5th ave',
                            'Partner?': 'Yes',
                            'History': 'lorem'
                        }
                    },
                    {
                        'Place': {
                            'Name': 'Mary Doe',
                            'Title': 'Mrs.'
                        },
                        'Description': {
                            'Location': '6th ave',
                            'Partner?': '',
                            'History': 'ipsum'
                        }
                    },
                    ...
                ]
        '''
        row_values = self.worksheet.get_all_values()

        # Merged cells comes as empty strings. The loop below fills those cells
        # following an tree hierarchy to the left
        headers = row_values[:self.header_rows]
        if not headers[0][0]:
            return dict(errors=["Bad worksheet structure, cell A1 can't be empty"])
        for r in xrange(0, len(headers) - 1):  # the bottom row are leafs, disconsider it.
            for c in xrange(1, len(headers[r])):  # left most column can't be empty!
                if not headers[r][c]:
                    headers[r][c] = headers[r][c-1]

        # Build worksheet structure dict
        root = OrderedDict()
        for c in xrange(len(headers[r])):
            node = root
            for r in xrange(len(headers)):
                key = headers[r][c]
                if not key in node:
                    node[key] = OrderedDict()
                node = node[key]
        data_structure = root

        # Organize data rows following the structure given by the headers ones
        raw_data = row_values[self.header_rows:]
        rows_dicts = []  # list of object dicts
        for r in xrange(len(raw_data)):
            row_dict = deepcopy(data_structure)  # a object dict for each row
            for c in xrange(len(raw_data[r])):
                attr_value = raw_data[r][c]
                node = row_dict
                for hr in xrange(len(headers)):  # iterate over header rows
                    key = headers[hr][c]
                    if node[key] != {}:
                        node = node[key]  # not a leaf node, continue
                    else:
                        node[key] = attr_value  # copy attribute
            # give each interpreter the chance to organize the row_dict better
            rows_dicts.append(row_dict)

        return rows_dicts
    
    def row_dict_to_parse_dict(self, row_dict):
        '''
        Receives a row_dict and parses it to a parse_dict. See class docstring
        for more information on row_dict and parse_dict definitions.
        '''
        raise NotImplementedError('Subclass responsability')

    def object_dict_to_object(self, row_dict):
        '''
        Receives an object_dict and returns an object already saved to the
        database. See class docstring for more information on object_dict
        definition.
        '''
        raise NotImplementedError('Subclass responsability')

    def parse(self):
        '''
        Parses each row_dict into a dict containing the object, its warnings
        and its errors. Return a list with all of these dictionaries.
        '''
        parse_dicts = []
        for row_dict in self.get_row_dicts():
            parse_dicts.append(self.validate_row_dict(row_dict))
        return parse_dicts

    def insert(self, parse_dicts):
        '''
        Tries to insert all objects into the system atomically. If any error
        occurs no object is inserted.
        '''
        any_error = reduce(lambda a, b: a or b,
                        [bool(od['errors']) for od in parse_dicts])
        if any_error:
            return False, parse_dicts

        objs = []
        for od in [pd['object_dict'] for pd in parse_dicts]:
            o = self.object_dict_to_object(od)
            objs.append(o)

        return True, objs
