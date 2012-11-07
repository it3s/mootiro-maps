# -*- coding: utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings

import gspread


class BulkImport(models.Model):
    '''
    lalala
    '''

    name = models.CharField(max_length=256, null=False)
    description = models.TextField(null=True)
    key = models.CharField(max_length=, null=False)

    creator = models.ForeignKey(User, editable=False, null=False)
    creation_date = models.DateTimeField(auto_now_add=True)

    @property
    def spreadsheet(self):
        if not hasattr(self, '_spreadsheet'):
            client = gspread.login(settings.BULK_IMPORT_GOOGLE_USER,
                                   settings.BULK_IMPORT_GOOGLE_PASSWORD)
            self._spreadsheet = client.open_by_key(skey)
        return self._spreadsheet


class Spreadsheet(gspread.Spreadsheet):
    '''
    This classes extends gspread.model.Spreadsheet functionalities.
    '''


