# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from markitup.widgets import MarkItUpWidget
from fileupload.forms import FileuploadField
from fileupload.models import UploadedFile
from ajaxforms import AjaxModelForm

from main.utils import MooHelper, clean_autocomplete_field
from main.widgets import TaggitWidget, AutocompleteWithFavorites
from ajax_select.fields import AutoCompleteSelectMultipleField
from komoo_resource.models import Resource, ResourceKind
from signatures.signals import notify_on_update

logger = logging.getLogger(__name__)


class FormResource(AjaxModelForm):
    description = forms.CharField(widget=MarkItUpWidget())
    kind = forms.CharField(required=False, widget=AutocompleteWithFavorites(
            ResourceKind, '/resource/search_by_kind/',
            ResourceKind.favorites(number=10), can_add=True))
    contact = forms.CharField(required=False, widget=MarkItUpWidget())
    tags = forms.Field(required=False, widget=TaggitWidget(
            autocomplete_url="/resource/search_tags/"))
    community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)
    files = FileuploadField(required=False)

    class Meta:
        model = Resource
        fields = ('name', 'description', 'kind', 'contact', 'tags', 'community',
            'id', 'files')

    _field_labels = {
        'name': _('Name'),
        'description': _('Description'),
        'kind': _('Kind'),
        'contact': _('Contact'),
        'tags': _('Tags'),
        'community': _('Community'),
        'files': '', }

    def __init__(self, *args, **kwargs):
        self.helper = MooHelper(form_id='form_resource')
        r = super(FormResource, self).__init__(*args, **kwargs)
        self.fields['name'].initial = ''
        return r

    @notify_on_update
    def save(self, *args, **kwargs):
        resource = super(FormResource, self).save(*args, **kwargs)
        UploadedFile.bind_files(
            self.cleaned_data.get('files', '').split('|'), resource)
        return resource

    def clean_kind(self):
        return clean_autocomplete_field(
            self.cleaned_data['kind'], ResourceKind)


class FormResourceGeoRef(FormResource):
    geometry = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Resource
        fields = ('name', 'description', 'kind', 'contact', 'tags', 'community',
            'id', 'geometry', 'files')
