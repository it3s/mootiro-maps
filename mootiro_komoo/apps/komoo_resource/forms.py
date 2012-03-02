# -*- coding: utf-8 -*-
from django import forms
from main.utils import MooHelper
from komoo_resource.models import Resource


class FormResource(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Resource
        fields = ['name', 'description', 'id', ]

    def __init__(self, *args, **kwargs):
        # Crispy forms configuration
        self.helper = MooHelper()
        self.helper.form_id = 'form_resource'

        super(FormResource, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(FormResource, self).save(*args, **kwargs)
