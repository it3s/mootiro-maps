# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from markitup.widgets import MarkItUpWidget
from fileupload.forms import FileuploadField, SingleFileUploadWidget
from fileupload.models import UploadedFile
from ajax_select.fields import AutoCompleteSelectMultipleField
from ajaxforms import AjaxModelForm

from main.utils import MooHelper, clean_autocomplete_field
from main.widgets import TaggitWidget
from .models import Project

logger = logging.getLogger(__name__)


class FormProject(AjaxModelForm):
    description = forms.CharField(widget=MarkItUpWidget())
    contact = forms.CharField(required=False, widget=MarkItUpWidget())
    tags = forms.Field(required=False, widget=TaggitWidget(
        autocomplete_url="/project/search_tags/"))
    community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)
    contributors = AutoCompleteSelectMultipleField('user', help_text='',
        required=False)
    logo = FileuploadField(required=False, widget=SingleFileUploadWidget)
    partners_logo = FileuploadField(required=False)

    class Meta:
        model = Project
        fields = ('name', 'description', 'contributors', 'tags', 'contact',
                  'community', 'logo', 'id')

    _field_labels = {
        'name': _('Name'),
        'description': _('Description'),
        'tags': _('Tags'),
        'logo': _('Logo'),
        'contact': _('Contact'),
        'contributors': _('Contributors'),
        'community': _('Community'),
        'partners_logo': _('Partners Logo'),
    }

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id='form_project')
        return super(FormProject, self).__init__(*a, **kw)

    def save(self, *a, **kw):
        proj = super(FormProject, self).save(*a, **kw)
        UploadedFile.bind_files(
                self.cleaned_data.get('partners_logo', '').split('|'), proj)
        return proj

    def clean_logo(self):
        return clean_autocomplete_field(self.cleaned_data['logo'],
                                        UploadedFile)


