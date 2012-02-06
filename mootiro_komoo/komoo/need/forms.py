#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django import forms

from komoo.need.models import Need


class NeedForm(forms.Form):


    class Media:
        js = ('jquery-1.7.1.js', 'jquery-ui-1.8.16.min')
