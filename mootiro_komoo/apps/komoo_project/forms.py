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


PUBLIC_CHOICES = (
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
    public = forms.ChoiceField(choices=PUBLIC_CHOICES,
            widget=forms.RadioSelect)
    public_discussion = forms.ChoiceField(choices=PUBLIC_CHOICES,
            widget=forms.RadioSelect)

    class Meta:
        model = Project
        fields = ('name', 'description', 'contributors', 'tags', 'contact',
                  'community', 'public', 'public_discussion', 'logo', 'id')

    _field_labels = {
        'name': _('Name'),
        'description': _('Description'),
        'tags': _('Tags'),
        'logo': _('Logo'),
        'contact': _('Contact'),
        'contributors': _('Contributors'),
        'community': _('Community'),
        'partners_logo': _('Partners Logo'),
        'public': _('Access to edit this project'),
        'public_discussion': _('Access to this project\'s discussion page'),
    }

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id='form_project')
        inst = kw.get('instance', None)
        if inst:
            public = 'publ' if inst.public else 'priv'
            public_discussion = 'publ' if inst.public_discussion else 'priv'
        else:
            public, public_discussion = 'publ', 'priv'
        kw['initial'] = {
                'public': public, 'public_discussion': public_discussion}
        return super(FormProject, self).__init__(*a, **kw)

    def save(self, *a, **kw):
        proj = super(FormProject, self).save(*a, **kw)
        UploadedFile.bind_files(
                self.cleaned_data.get('partners_logo', '').split('|'), proj)
        return proj

    def clean_logo(self):
        return clean_autocomplete_field(self.cleaned_data['logo'],
                                        UploadedFile)

    def clean_public(self):
        return True if self.cleaned_data['public'] == 'publ' else False

    def clean_public_discussion(self):
            return True if self.cleaned_data['public_discussion'] == 'publ' \
                        else False
