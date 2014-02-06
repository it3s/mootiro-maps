# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import json

from django import forms
from django.utils.translation import ugettext_lazy as _

from markitup.widgets import MarkItUpWidget
from fileupload.forms import FileuploadField
from fileupload.models import UploadedFile
from ajaxforms import AjaxModelForm
from annoying.functions import get_object_or_None

from main.utils import MooHelper
from main.widgets import TaggitWidget, AutocompleteWithFavorites, ContactsWidget
from ajax_select.fields import AutoCompleteSelectMultipleField
from komoo_resource.models import Resource, ResourceKind
from komoo_project.models import Project
from signatures.signals import notify_on_update
from video.forms import VideosField
from video.models import Video

logger = logging.getLogger(__name__)


class FormResource(AjaxModelForm):
    class Meta:
        model = Resource
        fields = ('id', 'name', 'short_description', 'description', 'contacts',
                  'tags', 'kind', 'community', 'files', 'videos', 'project_id')

    _field_labels = {
        'name': _('Name'),
        'short_description': _('Short description'),
        'description': _('Description'),
        'contacts': _('Contacts'),
        'tags': _('Tags'),
        'kind': _('Content type'),
        'community': _('Community'),
        'files': _('Images'),
        'videos': _('Videos'),
    }

    description = forms.CharField(widget=MarkItUpWidget())
    contacts = forms.CharField(required=False, widget=ContactsWidget())
    tags = forms.Field(required=False, widget=TaggitWidget(
            autocomplete_url="/resource/search_tags/"))
    kind = forms.CharField(required=False, widget=AutocompleteWithFavorites(
            ResourceKind, '/resource/search_by_kind/',
            ResourceKind.favorites(number=10), can_add=True))
    community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)
    files = FileuploadField(required=False)
    videos = VideosField(required=False)
    project_id = forms.CharField(widget=forms.HiddenInput(), required=False)

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

        videos = json.loads(self.cleaned_data.get('videos', ''))
        Video.save_videos(videos, resource)

        # Add the community to project if a project id was given.
        project_id = self.cleaned_data.get('project_id', None)
        if project_id:
            project = get_object_or_None(Project, pk=int(project_id))
            if project:
                project.save_related_object(resource, self.user)

        return resource

    def clean_kind(self):
        field_data = self.cleaned_data['kind']
        model = ResourceKind
        can_add = self.fields['kind'].widget.can_add
        try:
            if not field_data or field_data == 'None':
                if can_add and self.data.get('kind_autocomplete', ''):
                    new_kind = model(name=self.data['kind_autocomplete'])
                    new_kind.save()
                    return new_kind
                else:
                    return model()
            else:
                return model.objects.get(pk=field_data)
        except:
            raise forms.ValidationError(_('invalid field data'))


class FormResourceGeoRef(FormResource):
    geometry = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Resource
        fields = ('id', 'name', 'short_description', 'description', 'contacts',
                  'tags', 'kind', 'community', 'files', 'videos', 'project_id',
                  'geometry')

