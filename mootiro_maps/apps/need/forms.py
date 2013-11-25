#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django import forms
from django.utils.translation import ugettext_lazy as _
from markitup.widgets import MarkItUpWidget
from fileupload.forms import FileuploadField
from fileupload.models import UploadedFile
from ajaxforms import AjaxModelForm
from annoying.functions import get_object_or_None

from main.utils import MooHelper
from main.widgets import Tagsinput, TaggitWidget, ImageSwitchMultiple
from ajax_select.fields import AutoCompleteSelectMultipleField
from need.models import Need, NeedCategory, TargetAudience
from komoo_project.models import Project
from signatures.signals import notify_on_update
from video.forms import VideosField


need_form_fields = ('id', 'title', 'short_description', 'description',
                    'community', 'categories', 'target_audiences', 'tags',
                    'files', 'project_id')

need_form_field_labels = {
    'title': _('Title'),
    'short_description': _('Short description'),
    'description': _('Description'),
    'community': _('Community'),
    'categories': _('Need categories'),
    'target_audiences': _('Target audiences'),
    'tags': _('Tags'),
    'files': _('Images'),
}


class NeedForm(AjaxModelForm):
    class Meta:
        model = Need
        fields = need_form_fields

    _field_labels = need_form_field_labels

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

    videos = VideosField(required=False)

    project_id = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id="need_form")
        return super(NeedForm, self).__init__(*a, **kw)

    @notify_on_update
    def save(self, *args, **kwargs):
        need = super(NeedForm, self).save(*args, **kwargs)
        UploadedFile.bind_files(
            self.cleaned_data.get('files', '').split('|'), need)

        # Add the community to project if a project id was given.
        project_id = self.cleaned_data.get('project_id', None)
        if project_id:
            project = get_object_or_None(Project, pk=int(project_id))
            if project:
                project.save_related_object(need, self.user)

        return need


class NeedFormGeoRef(NeedForm):
    class Meta:
        model = Need
        fields = need_form_fields + ('geometry',)

    _field_labels = need_form_field_labels

    geometry = forms.CharField(widget=forms.HiddenInput())
