# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from markitup.widgets import MarkItUpWidget
from main.utils import MooHelper
from main.widgets import Autocomplete
from komoo_resource.models import Resource, ResourceKind


class FormResource(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    description = forms.CharField(widget=MarkItUpWidget())
    kind = forms.CharField(
        widget=Autocomplete(ResourceKind, '/resource/search_by_kind/'))

    class Meta:
        model = Resource
        fields = ['name', 'description', 'kind', 'id']

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

    def clean_kind(self):
        return ResourceKind.objects.get(id=self.cleaned_data['kind'])
