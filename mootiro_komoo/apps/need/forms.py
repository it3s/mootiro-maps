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
from main.widgets import Tagsinput, TaggitWidget, ImageSwitchMultiple
from ajax_select.fields import AutoCompleteSelectMultipleField
from need.models import Need, NeedCategory, TargetAudience


class NeedForm(AjaxModelForm):
    class Meta:
        model = Need
        fields = ('community', 'title', 'description', 'categories',
                    'target_audiences', 'tags', 'files')

    _field_labels = {
        'community': _('Community'),
        'title': _('Title'),
        'description': _('Description'),
        'categories': _('Categories'),
        'target_audiences': _('Target audiences'),
        'tags': _('Tags'),
        'files': _(' '),
    }

    class Media:
        js = ('lib/jquery.imagetick-original.js',)

    community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)

    description = forms.CharField(widget=MarkItUpWidget())

    categories = forms.ModelMultipleChoiceField(
        queryset=NeedCategory.objects.all().order_by('name'),
        widget=ImageSwitchMultiple(
            get_image_tick=NeedCategory.get_image,
            get_image_no_tick=NeedCategory.get_image_off
        )
    )

    target_audiences = forms.Field(
        widget=Tagsinput(
            TargetAudience,
            autocomplete_url="/need/target_audience_search")
    )

    tags = forms.Field(
        widget=TaggitWidget(autocomplete_url="/need/tag_search"),
        required=False
    )

    files = FileuploadField(required=False)

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id="need_form")
        return super(NeedForm, self).__init__(*a, **kw)

    # def clean_community(self):
    #     value = self.cleaned_data['community']
    #     return Community.objects.get(id=value) if value else value

    def save(self, *args, **kwargs):
        need = super(NeedForm, self).save(*args, **kwargs)
        UploadedFile.bind_files(
            self.cleaned_data.get('files', '').split('|'), need)
        return need


class NeedFormGeoRef(NeedForm):
    class Meta:
        model = Need
        fields = ('community', 'title', 'description', 'categories',
                    'target_audiences', 'tags', 'geometry', 'files')

    _field_labels = {
        'community': _('Community'),
        'title': _('Title'),
        'description': _('Description'),
        'categories': _('Categories'),
        'target_audiences': _('Target audiences'),
        'tags': _('Tags'),
        'files': _(' '),
    }

    geometry = forms.CharField(widget=forms.HiddenInput())
