# -*- coding: utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings

from authentication.models import User
from projects.models import Project

import gspread
from interpreters import InterpreterFactory

from .google import google_drive_service


class Importsheet(models.Model):
    '''
    Represents a google spreadsheet used to import objects into the database.
    It interacts with google APIs and stores all information needed to do so.
    '''
    name = models.CharField(max_length=256, null=False)
    description = models.TextField(null=True)
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
            self._spreadsheet = client.open_by_key(self.spreadsheet_key)
        return self._spreadsheet

    @classmethod
    def __new__(cls, *a, **kw):
        '''Creates new database object for the importsheet.'''
        if 'spreadsheet_key' in kw:
            raise KeyError('spreadsheet_key should not be provided it is \
                            automatically retrieved from google api.')
        obj = super(Importsheet, cls).__new__(cls, *a, **kw)
        return obj

    def __init__(self, *a, **kw):
        ret = super(Importsheet, self).__init__(*a, **kw)
        if not self.spreadsheet_key:
            self._set_google_spreadsheet()
        return ret

    def _set_google_spreadsheet(self):
        '''
        Using Google Drive API and Google Spreadsheet API, creates new google
        spreadsheet inside its project folder. If it is the projects first
        importsheet, also creates the projects folder. 

        The structure in Google Drive is the following:

        "Projects Root" (settings.IMPORTSHEET_PROJECTS_FOLDER_KEY)
          |- "project1.id - project1.name"
          |    |- "importsheet1.name"
          |    |- "importsheet2.name"
          |- "project2.id - project2.name"
          |    |- "importsheet3.name"
          ...
        '''
        # Google API objects handling
        gd = google_drive_service()
        
        # set project folder
        for ish in self.project.importsheets.all():
            if ish != self and ish.project_folder_key:
                # put importsheets in same folder for same project
                self.project_folder_key = ish.project_folder_key
                break
        if not self.project_folder_key:
            # project's first importsheet, create a new folder for it
            body = {
                'title': '{} - {}'.format(self.project.id, self.project.name),
                'parents': [{'id': settings.IMPORTSHEET_PROJECTS_FOLDER_KEY}],
                'mimeType': 'application/vnd.google-apps.folder',
            }
            data = gd.files().insert(body=body).execute()
            self.project_folder_key = data['id']

        # create new spreadsheet 
        body = {
            'title': self.name,
            'parents': [{'id': self.project_folder_key}],
        }
        data = gd.files().copy(fileId=settings.IMPORTSHEET_TEMPLATE_KEY,
                            body=body).execute()
        self.spreadsheet_key = data['id']

    def __unicode__(self):
        return self.name

    def simulate(self, worksheet_name):
        '''
        Receives a worksheet name, parses it, and returns a list of annotated
        dicts with errors and warnings.

        Example:
            ish = Importsheet(name='Schools Mapping', project=p, ...)
            ish.simulate('organization')
        '''
        worksheet = self.spreadsheet.worksheet(worksheet_name)
        interpreter = InterpreterFactory.make_interpreter(worksheet)
        objects_dicts, warnings_dicts, errors_dicts = interpreter.simulate()
        return {
            'objects': objects_dicts,
            'warnings': warnings_dicts,
            'errors': errors_dicts,
        }

    def process(self):
        '''
        Imports data from each one of the worksheets in the spreadsheet.

        Example:
            ish = Importsheet(name='Schools Mapping', project=p, ...)
            ish.process()
        '''
        for worksheet in self.spreadsheet.worksheets():
            interpreter = InterpreterFactory.make_interpreter(worksheet)
            for obj in interpreter.objects():
                # TODO: treat exceptions and integrity errors
                obj.save()
