#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.forms import ModelForm
from komoo.need.models import Need


class NeedForm(ModelForm):
    class Meta:
        model = Need
