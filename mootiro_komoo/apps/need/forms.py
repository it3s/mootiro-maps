#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django import forms
from markitup.widgets import MarkItUpWidget

from main.utils import MooHelper
from main.widgets import Autocomplete, Tagsinput, TaggitWidget, ImageSwitchMultiple
from need.models import Need, NeedCategory, TargetAudience
from community.models import Community


class NeedForm(forms.ModelForm):
    class Meta:
        model = Need
        fields = ('community', 'title', 'description', 'categories',
                    'target_audiences', 'tags', 'geometry')

    # FIXME: the urls below should not be hardcoded. They should be calculated
    # with reverse_lazy function, which is not implemented in Django 1.3 yet.
    # community = forms.CharField(
    #     widget=Autocomplete(Community, "/community/search_by_name"),
    #     required=False
    # )
    community = forms.ModelChoiceField(
        queryset=Community.objects.all(),
        widget=Autocomplete(Community, "/community/search_by_name"),
        required=False
    )

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

    geometry = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *a, **kw):
        # Crispy forms configuration
        self.helper = MooHelper()
        self.helper.form_id = "need_form"

        super(NeedForm, self).__init__(*a, **kw)

    # def clean_community(self):
    #     value = self.cleaned_data['community']
    #     return Community.objects.get(id=value) if value else value
