# -*- coding: utf-8 -*-
from django import forms
# from main.utils import MooHelper
from komoo_resource.models import Resource


class FormResource(forms.ModelForm):
    class Meta:
        model = Resource

    # def _init__(self, *args, **kwargs):
    #     # Crispy forms configuration
    #     self.helper = MooHelper()
    #     self.helper.form_id = 'form_resource'

    #     super(FormResource, self).__init__(*args, **kwargs)
