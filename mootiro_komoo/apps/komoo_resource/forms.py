# -*- coding: utf-8 -*-
from django import forms
from komoo_resource.models import Resource


class FormResource(forms.ModelForm):
    class Meta:
        model = Resource
