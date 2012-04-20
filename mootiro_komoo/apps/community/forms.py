#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django import forms
from markitup.widgets import MarkItUpWidget
from fileupload.forms import FileuploadField
from fileupload.models import UploadedFile

from main.utils import MooHelper
from community.models import Community


class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ('name', 'population', 'description', 'geometry', 'files')

    description = forms.CharField(widget=MarkItUpWidget())
    geometry = forms.CharField(widget=forms.HiddenInput())
    files = FileuploadField(required=False)

    def __init__(self, *a, **kw):
        # Crispy forms configuration
        self.helper = MooHelper()
        self.helper.form_id = "community_form"

        super(CommunityForm, self).__init__(*a, **kw)

    def save(self, *args, **kwargs):
        comm = super(CommunityForm, self).save(*args, **kwargs)
        files_id_list = self.cleaned_data.get('files', '').split('|')
        UploadedFile.bind_files(files_id_list, comm)
        return comm
