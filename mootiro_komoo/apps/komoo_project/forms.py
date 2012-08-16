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


IS_PUBLIC_CHOICES = (
        ('publ', _('Public')),
        ('priv', _('Private'))
)


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
    is_public = forms.ChoiceField(choices=IS_PUBLIC_CHOICES,
            widget=forms.RadioSelect)

    class Meta:
        model = Project
        fields = ('name', 'description', 'contributors', 'tags', 'contact',
                  'community', 'is_public', 'logo', 'id')

    _field_labels = {
        'name': _('Name'),
        'description': _('Description'),
        'tags': _('Tags'),
        'logo': _('Logo'),
        'contact': _('Contact'),
        'contributors': _('Contributors'),
        'community': _('Community'),
        'partners_logo': _('Partners Logo'),
        'is_public': _('Access to editing and discussion pages'),
    }

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id='form_project')
        inst = kw.get('instance', None)
        if inst:
            is_public = 'publ' if inst.is_public else 'priv'
        else:
            is_public = 'publ'
        kw['initial'] = {'is_public': is_public}
        return super(FormProject, self).__init__(*a, **kw)

    def save(self, *a, **kw):
        proj = super(FormProject, self).save(*a, **kw)
        UploadedFile.bind_files(
                self.cleaned_data.get('partners_logo', '').split('|'), proj)
        return proj

    def clean_logo(self):
        return clean_autocomplete_field(self.cleaned_data['logo'],
                                        UploadedFile)

    def clean_is_public(self):
        return True if self.cleaned_data['is_public'] == 'publ' else False
