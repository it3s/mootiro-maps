#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django import forms

from komoo_map.widgets import AddressWithMapWidget
from community.models import Community


class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community

    geometry = forms.CharField(widget=forms.HiddenInput())


class CommunityMapForm(forms.Form):
    map = forms.CharField(widget=AddressWithMapWidget, required=False)
