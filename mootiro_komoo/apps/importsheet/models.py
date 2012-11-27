# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from authentication.models import User
from komoo_project.models import Project

import gspread
from interpreters import InterpreterFactory, InterpreterNotFound

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
    inserted = models.BooleanField(default=False)

    # Google Spreadsheets API data
    spreadsheet_key = models.CharField(max_length=128, null=True)
    project_folder_key = models.CharField(max_length=128, null=True)

    def __unicode__(self):
        return self.name

    @property
    def spreadsheet(self):
        '''The gspread Spreadsheet instance of a importsheet.'''
        if not self.spreadsheet_key:
            raise Exception('Importsheet must be saved to database before '
                            'interacting with Google.')
        if not hasattr(self, '_spreadsheet'):
            client = gspread.login(settings.IMPORTSHEET_GOOGLE_USER,
                                   settings.IMPORTSHEET_GOOGLE_PASSWORD)
            self._spreadsheet = client.open_by_key(self.spreadsheet_key)
        return self._spreadsheet

    @property
    def worksheets(self):
        '''The gspread Worksheets recognized by any of the interpreters.'''
        l = []
        for worksheet in self.spreadsheet.worksheets():
            try:
                InterpreterFactory.make_interpreter(worksheet)
                l.append(worksheet)
            except InterpreterNotFound:
                pass  # worksheet not recognized
        return l

    @classmethod
    def __new__(cls, *a, **kw):
        '''Creates new database object for the importsheet.'''
        if 'spreadsheet_key' in kw:
            raise KeyError('spreadsheet_key should not be provided it is '
                           'automatically retrieved from google api.')
        obj = super(Importsheet, cls).__new__(cls, *a, **kw)
        return obj

    def save(self, *a, **kw):
        ret = super(Importsheet, self).save(*a, **kw)
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
          |    |- "importsheet1.id - importsheet1.name"
          |    |- "importsheet2.id - importsheet2.name"
          |- "project2.id - project2.name"
          |    |- "importsheet3.id - importsheet3.name"
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
            'title': '{0} - {1}'.format(self.id, self.name),
            'parents': [{'id': self.project_folder_key}],
        }
        data = gd.files().copy(fileId=settings.IMPORTSHEET_TEMPLATE_KEY,
                            body=body).execute()
        self.spreadsheet_key = data['id']
        self.save()

    def simulate(self, worksheet_name):
        '''
        Receives a worksheet name, parses it, and returns a list of annotated
        dicts with errors and warnings.

        Example:

            ish = Importsheet(name='Schools Mapping', project=p, ...)
            ish.simulate('organization')
        '''
        worksheet = self.spreadsheet.worksheet(worksheet_name)
        worksheet_interpreter = InterpreterFactory.make_interpreter(worksheet)
        worksheet_interpreter.parse()
        return worksheet_interpreter

    def insert_all(self):
        if self.inserted:
            success = True
            return success

        success = True
        for wks in self.worksheets:
            success = success and self.insert(wks.title)
        return success


    def insert(self, worksheet_name):
        '''
        Imports data from each one of the worksheets in the spreadsheet.

        Example:

            ish = Importsheet(name='Schools Mapping', project=p, ...)
            ish.insert()
        '''

        worksheet = self.spreadsheet.worksheet(worksheet_name)
        interpreter = InterpreterFactory.make_interpreter(worksheet)
        success = interpreter.insert()
        if success:
            # link objects to importsheet and to project
            for obj in interpreter.objects:
                self.project.save_related_object(obj)
                self.save_related_object(obj)
                obj.save()
            self.inserted = True
            self.save()

        return success

    @property
    def inserted_objects(self):
        '''Returns a list of all related objects.'''
        related_objects = ImportsheetRelatedObject.objects.filter(importsheet=self)
        return [iro.content_object for iro in related_objects]

    def save_related_object(self, related_object):
        ct = ContentType.objects.get_for_model(related_object)
        iro, created = ImportsheetRelatedObject.objects.get_or_create(
                            object_id=related_object.id,
                            content_type_id=ct.id,
                            importsheet_id=self.id)
        return created


class ImportsheetRelatedObject(models.Model):
    importsheet = models.ForeignKey('Importsheet')

    # dynamic ref
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
