# -*- coding: utf8 -*-
from __future__ import unicode_literals

import gspread
from copy import deepcopy


class Interpreter(gspread.Worksheet):
    '''
    Interface for each worksheet type interpreter.
    '''

    def __init__(self, gspread_worksheet):
        self.worksheet = gspread_worksheet

    def get_rows_dicts(self):
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
        root = {}
        for c in xrange(len(headers[r])):
            node = root
            for r in xrange(len(headers)):
                key = headers[r][c]
                if not key in node:
                    node[key] = {}
                node = node[key]
        data_structure = root

        # Organize data rows following the structure given by the headers ones
        raw_data = row_values[self.header_rows:]
        objects = []  # list of object dicts
        for r in xrange(len(raw_data)):
            obj = deepcopy(data_structure)  # a object dict for each row
            for c in xrange(len(raw_data[r])):
                attr_value = raw_data[r][c]
                node = obj
                for hr in xrange(len(headers)):  # iterate over header rows
                    key = headers[hr][c]
                    if node[key] != {}:
                        node = node[key]  # not a leaf node, continue
                    else:
                        node[key] = attr_value  # copy attribute
            objects.append(obj)

        return objects
