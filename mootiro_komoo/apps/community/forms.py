#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import json

from django import forms
from markitup.widgets import MarkItUpWidget

from main.utils import MooHelper
from komoo_map.widgets import AddressWithMapWidget
from community.models import Community


class GeoJSONField(forms.CharField):
    widget = forms.HiddenInput

    def to_python(self, value):
        value = json.loads(value)
        if value.has_key('geometries'):
            value = value['geometries'][0]
        return json.dumps(value)

    def prepare_value(self, value):
        if hasattr(value, 'geojson'):
            value = value.geojson
        return value


class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community

    description = forms.CharField(widget=MarkItUpWidget())
    geometry = GeoJSONField()

    def __init__(self, *a, **kw):
        # Crispy forms configuration
        self.helper = MooHelper()
        self.helper.form_id = "community_form"

        super(CommunityForm, self).__init__(*a, **kw)


class CommunityMapForm(forms.Form):
    map = forms.CharField(widget=AddressWithMapWidget, required=False)
