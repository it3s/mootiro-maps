#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django import forms

from komoo.widgets import JQueryAutoComplete
from komoo.need.models import Need
from komoo.community.models import Community


class NeedForm(forms.ModelForm):
    class Meta:
        model = Need

    community_slug = forms.CharField(widget=forms.HiddenInput())
    community = forms.CharField(widget=JQueryAutoComplete("/community/search_by_name",
        value_field='community_slug'))

    def clean_community_slug(self):
        self.cleaned_data['community'] = Community.objects \
            .get(slug=self.cleaned_data['community_slug'])
