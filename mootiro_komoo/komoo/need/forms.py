#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django import forms
from django.core.urlresolvers import reverse
from komoo.widgets import JQueryAutoComplete
from komoo.need.models import Need


class NeedForm(forms.ModelForm):
    class Meta:
        model = Need

    community = forms.CharField(widget=JQueryAutoComplete("/community/search_by_name"))

