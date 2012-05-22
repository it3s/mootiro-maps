#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django import forms
from django.utils.translation import ugettext_lazy as _
from markitup.widgets import MarkItUpWidget
from fileupload.forms import FileuploadField
from fileupload.models import UploadedFile
from ajaxforms import AjaxModelForm

from main.utils import MooHelper
from main.widgets import TaggitWidget
from community.models import Community


class CommunityForm(AjaxModelForm):
    class Meta:
        model = Community
        fields = ('name', 'population', 'description', 'tags', 'geometry',
                  'files')

    _field_labels = {
        'name': _('Name'),
        'description': _('Description'),
        'population': _('Population'),
        'tags': _('Tags'),
        'files': _(' '),
    }

    description = forms.CharField(widget=MarkItUpWidget())
    geometry = forms.CharField(widget=forms.HiddenInput())
    files = FileuploadField(required=False)
    tags = forms.Field(
        widget=TaggitWidget(autocomplete_url="/community/search_by_tag/"),
        required=False)

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id="community_form")
        return super(CommunityForm, self).__init__(*a, **kw)

    def save(self, *args, **kwargs):
        comm = super(CommunityForm, self).save(*args, **kwargs)
        UploadedFile.bind_files(
            self.cleaned_data.get('files', '').split('|'), comm)
        return comm
