# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext as _

import gspread
from copy import deepcopy
from collections import OrderedDict

from ..google import google_fusion_tables_service


class Interpreter(object):
    '''
    Interface class for each **worksheet** type interpreter.

    IMPORTANT CONCEPTS:
      row_dict: a dictionary with information from the worksheet indexed with
        its header lines. (see get_rows_dicts method)

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
        row_interpreter = MyAwesomeRowInterpreter
        row_template = 'importsheet/row_templates/myawesome.html'


    class MyAwesomeRowInterpreter(RowInterpreter):
        def parse_row_dict(self, row_dict):
            ...

        def to_object(self, row_dict):
            ...
    '''

    def __init__(self, importsheet, gspread_worksheet):
        self.importsheet = importsheet
        self.worksheet = gspread_worksheet
        self.rows = []
        self.kml_dicts = []
        self.errors = []
        self.warnings = []

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
                if key == '':
                    continue
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
                    if key == '':
                        continue
                    if node[key] != {}:
                        node = node[key]  # not a leaf node, continue
                    else:
                        node[key] = attr_value  # copy attribute
                        break  # shorter branches may stop earlier
                if node == row_dict:  # no header string found
                    cletter = self.worksheet.get_addr_int(r + 1, c + 1)[0]
                    msg = _('Column {cletter} ignored due to an empty header.')\
                            .format(cletter=cletter)
                    if not msg in self.warnings:
                        self.warnings.append(msg)

            # give each interpreter the chance to organize the row_dict better
            rows_dicts.append(row_dict)

        return rows_dicts

    def get_kml_dicts(self):
        '''
        Get data from Google Fusion Tables and builds a dict representing 
        the kml data.
        '''
        if not self.importsheet.kml_import:
            self.kml_dicts = {}
            return

        if self.kml_dicts:
            return

        gft = google_fusion_tables_service()
        query = 'SELECT * FROM {}'.format(self.importsheet.fusion_table_key)
        data = gft.query().sql(sql=query).execute()
        
        cols = data['columns']
        self.kml_dicts = [{cols[i]:row[i] for i in range(len(cols))} \
                            for row in data['rows']]

        counting = {}
        for pid in [kd['Identificador do polígono'] for kd in self.kml_dicts]:
            if not pid in counting:
                counting[pid] = 0
            counting[pid] += 1
        for pid, count in counting.items():
            if count > 1:
                msg = _('Duplicate polygon identifier in Fusion Table: {}') \
                        .format(pid)
                self.errors.append(msg)

        return self.kml_dicts

    # TODO: change default to parse_kml=False
    def parse(self, parse_kml=True):
        '''
        Parses each row_dict into a dict containing the object, its warnings
        and its errors. Return a list with all of these dictionaries.
        '''
        if parse_kml:
            self.get_kml_dicts()  # this sets self.kml_dicts
        for row_dict in self.get_row_dicts():
            ri = self.row_interpreter(row_dict, self.kml_dicts)
            try:
                ri.parse()
            except KeyError as e:
                msg = _('Missing column: {0}').format(e.message)
                self.errors.append(msg)
                self.rows = []
                break
            self.rows.append(ri)

        # discover two objects with same name in spreadsheet
        names = [r.object_dict['name'] for r in self.rows]
        names_count = {n:names.count(n) for n in names}
        for n, c in names_count.items():
            if c > 1:
                msg = _('{} objects to be imported with same name: {}') \
                        .format(c, n)
                self.errors.append(msg)

    def insert(self):
        '''
        Tries to insert all objects into the system atomically. If any error
        occurs no object is inserted. Returns a boolean indicating if the
        process succeded.
        '''
        self.parse()
        any_error = reduce(lambda a, b: a or b,
                            [bool(ri.errors) for ri in self.rows] or [False])
        if any_error:
            return False

        # TODO: should use database transaction rollback control in lines below
        #       for recover of partial objects insert
        self.objects = []
        for row in self.rows:
            o = row.to_object()
            self.objects.append(o)

        return True


class RowInterpreter(object):
    '''
    IMPORTANT CONCEPTS:

      row_dict: (see Interpreter.get_rows_dicts method)

      object_dict: a dictionary constructed based on a row_dict. It has just
        one level and its keys are the objects attributes.

      errors: a list of error messages (strings)

      warnings: a list of warning messages (strings)
    '''

    def __init__(self, row_dict, kml_dicts):
        self.row_dict = row_dict
        self.kml_dicts = kml_dicts

    def parse(self):
        '''
        Expects self.row_dict to be set, parses its information, and defines
        the following attributes to self:

            self.object_dict = {...}
            self.errors = [...]
            self.warnings = [...]

        Returns None. See class docstring for more information on the dicts
        defined above.
        '''
        raise NotImplementedError('Subclass responsability')

    def to_object(self):
        '''
        Expects self.object_dict to be set (what is done by calling
        parse_row_dict method), and returns an Model object filled with its
        information and already saved to database.
        '''
        raise NotImplementedError('Subclass responsability')
