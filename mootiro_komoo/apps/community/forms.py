#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default


from django import forms
from markitup.widgets import MarkItUpWidget

from main.utils import MooHelper
from komoo_map.widgets import AddressWithMapWidget
from community.models import Community


class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ('name', 'population', 'description', 'geometry')

    description = forms.CharField(widget=MarkItUpWidget())
    geometry = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *a, **kw):
        # Crispy forms configuration
        self.helper = MooHelper()
        self.helper.form_id = "community_form"

        super(CommunityForm, self).__init__(*a, **kw)


class CommunityMapForm(forms.Form):
    map = forms.CharField(widget=AddressWithMapWidget, required=False)
