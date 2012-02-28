#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset

from main.widgets import Autocomplete, Tagsinput, TaggitWidget, ImageSwitchMultiple
from need.models import Need, NeedCategory, TargetAudience
from community.models import Community


class MooHelper(FormHelper):
    def __init__(self, *a, **kw):
        super(MooHelper, self).__init__(*a, **kw)
        self.add_input(Submit('submit', 'Submit'))
        self.add_input(Reset('reset', 'Reset'))


class NeedForm(forms.ModelForm):
    class Meta:
        model = Need

    # FIXME: the urls below should not be hardcoded. They should be calculated
    # with reverse_lazy function, which is not implemented in Django 1.3 yet.
    community = forms.CharField(
        widget=Autocomplete("/community/search_by_name")
    )

    categories = forms.ModelMultipleChoiceField(
        queryset=NeedCategory.objects.all(),
        widget=ImageSwitchMultiple(
            get_image_tick=NeedCategory.get_image_tick,
            get_image_no_tick=NeedCategory.get_image_no_tick
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

    def __init__(self, *a, **kw):
        self.helper = MooHelper()
        super(NeedForm, self).__init__(*a, **kw)
        # self.is_bound does not work properly with ModelForm
        if 'instance' in kw and kw['instance']:
            self.fields.pop('community')

    def clean_community(self):
        return Community.objects.get(id=self.cleaned_data['community'])
