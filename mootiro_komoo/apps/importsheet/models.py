# -*- coding: utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings

from authentication.models import User
from projects.models import Project

import gspread
from copy import deepcopy


class Importsheet(models.Model):
    '''
    Represents a google spreadsheet used to import objects into the database.
    It interacts with google APIs and stores all information needed to do so.
    '''
    name = models.CharField(max_length=256, null=False)
    description = models.TextField(null=False)
    project = models.ForeignKey(Project, editable=False, null=False,
                                    related_name='importsheets')
    creator = models.ForeignKey(User, editable=False, null=False,
                                    related_name='created_importsheets')
    creation_date = models.DateTimeField(auto_now_add=True)

    # Google Spreadsheets API data
    spreadsheet_key = models.CharField(max_length=128, null=True)
    project_folder_key = models.CharField(max_length=128, null=True)

    @property
    def spreadsheet(self):
        '''The gspread Spreadsheet instance of a importsheet.'''
        if not hasattr(self, '_spreadsheet'):
            client = gspread.login(settings.IMPORTSHEET_GOOGLE_USER,
                                   settings.IMPORTSHEET_GOOGLE_PASSWORD)
            self._spreadsheet = client.open_by_key(self.key)
        return self._spreadsheet

    @classmethod
    def __new__(cls, *a, **kw):
        '''Creates new database object and the needed objects on Google API.'''
        if 'spreadsheet_key' in kw:
            raise KeyError('spreadsheet_key should not be provided it is \
                            automatically retrieved from google api.')
        # database object creation
        obj = super(Importsheet, cls).__new__(cls, *a, **kw)
        
        # Google API objects handling
        gd = google_drive_service(request)
        
        # set project folder
        for ish in obj.project.importsheets:
            if ish != obj and ish.project_folder_key:
                # put importsheets in same folder for same project
                obj.project_folder_key = ish.project_folder_key
                break
        if not obj.project_folder_key:
            # project's first importsheet, create a new folder for it
            body = {
                'title': '{} - {}'.format(obj.project.id, obj.project.name),
                'parents': [{'id': settings.IMPORTSHEET_PROJECTS_FOLDER_KEY}],
                'mimeType': 'application/vnd.google-apps.folder',
            }
            data = gd.files().insert(body=body).execute()
            obj.project_folder_key = data['id']

        # create new spreadsheet 
        body = {
            'title': obj.name,
            'parents': [{'id': data['id']}],
        }
        data = gd.files().copy(fileId=settings.IMPORTSHEET_TEMPLATE_KEY,
                            body=body).execute()
        obj.spreadsheet_key = data['id']

        return obj

    def simulate(self, worksheet_key):
        
        # verifica se a worksheet pertence a spreadsheet
        # adivinha (?) qual é o interpretador da worksheet
        # delega para ele a interpretação passando a worksheet

        pass


class WorksheetInterpreter(gspread.Worksheet):
    '''
    Interface for each worksheet type interpreter.
    '''
    @classmethod
    def get_records_tree(self, worksheet, header_rows=2):
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

            get_records_tree(worksheet, header_rows=2) ->
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
        row_values = worksheet.get_all_values()

        # Merged cells comes as empty strings. The loop below fills those cells
        # following an tree hierarchy to the left
        headers = row_values[:header_rows]
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
        raw_data = row_values[header_rows:]
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

class OrganizationWorksheet(WorksheetInterpreter):
    pass
