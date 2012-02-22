#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset

from main.fields import TagsField
from main.widgets import JQueryAutoComplete, Tagsinput, ImageSwitchMultiple
from need.models import Need, NeedCategory
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
        widget=JQueryAutoComplete("/community/search_by_name")
    )

    categories = forms.ModelMultipleChoiceField(
        queryset=NeedCategory.objects.all(),
        widget=ImageSwitchMultiple
    )

    tags = TagsField(widget=Tagsinput(autocomplete_url="/need/tag_search"))

    def __init__(self, *a, **kw):
        self.helper = MooHelper()
        super(NeedForm, self).__init__(*a, **kw)
        if 'instance' in kw and kw['instance']:  # self.is_bound does not work properly with ModelForm
            self.fields.pop('community')

    def clean_community(self):
        return Community.objects.get(id=self.cleaned_data['community'])
