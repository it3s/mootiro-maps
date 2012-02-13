#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django import forms

from komoo.fields import TagsField
from komoo.widgets import JQueryAutoComplete, Tagsinput
from komoo.need.models import Need, NeedCategory
from komoo.community.models import Community


class NeedForm(forms.ModelForm):
    class Meta:
        model = Need

    community_slug = forms.CharField(widget=forms.HiddenInput())
    # FIXME: the urls below should not be hardcoded. They should be calculated with
    # reverse_lazy function, which is not implemented in Django 1.3 yet.
    community = forms.CharField(widget=JQueryAutoComplete("/community/search_by_name",
        value_field='community_slug'))

    categories = forms.ModelMultipleChoiceField(
                    queryset=NeedCategory.objects.all(),
                    widget=forms.CheckboxSelectMultiple)

    tags = TagsField(widget=Tagsinput(autocomplete_url="/need/tag_search"))

    def clean_community_slug(self):
        self.cleaned_data['community'] = Community.objects \
            .get(slug=self.cleaned_data['community_slug'])
