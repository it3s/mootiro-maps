#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.forms import ModelForm, Form, CharField
from komoo_map.widgets import AddressWithMapWidget
from models import Community


class CommunityForm(ModelForm):
    class Meta:
        model = Community


class CommunityMapForm(Form):
    map = CharField(widget=AddressWithMapWidget, required=True)
