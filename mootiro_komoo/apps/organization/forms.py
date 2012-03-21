# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from organization.models import Organization


class FormOrganization(forms.ModelForm):
    class Meta:
        model = Organization
