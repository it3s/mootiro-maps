# -*- coding: utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings

from authentication.models import User
from projects.models import Project

import gspread


class Importsheet(models.Model):
    '''
    lalala

    bki = Importsheet(name=name, description=description)

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


class Spreadsheet(gspread.Spreadsheet):
    '''
    This classes extends gspread.Spreadsheet functionalities.
    '''
    pass
