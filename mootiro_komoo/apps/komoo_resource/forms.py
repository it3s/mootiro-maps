# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from main.utils import MooHelper
from komoo_resource.models import Resource


class FormResource(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Resource
        fields = ['name', 'description', 'id']

    def __init__(self, *args, **kwargs):
        # Crispy forms configuration
        self.helper = MooHelper()
        self.helper.form_id = 'form_resource'

        super(FormResource, self).__init__(*args, **kwargs)

    def save(self, user=None, *args, **kwargs):
        resource = super(FormResource, self).save(*args, **kwargs)
        if user and not user.is_anonymous():
            resource.creator_id = user.id
            resource.save()
        return resource
