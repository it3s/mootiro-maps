# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from markitup.widgets import MarkItUpWidget

from main.utils import MooHelper
from importsheet.models import Importsheet


class FormImportsheet(forms.Form):
    name = forms.CharField(required=True)
    description = forms.CharField(widget=MarkItUpWidget())
    project_id = forms.CharField(required=True)
    kml_import = forms.BooleanField(required=False)

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id="importsheet_form")
        return super(FormImportsheet, self).__init__(*a, **kw)
