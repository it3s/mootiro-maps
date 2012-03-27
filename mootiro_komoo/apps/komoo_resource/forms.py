# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from markitup.widgets import MarkItUpWidget

from main.utils import MooHelper
from main.widgets import Autocomplete, TaggitWidget, AutocompleteWithFavorites
from komoo_resource.models import Resource, ResourceKind
from community.models import Community


class FormResource(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    description = forms.CharField('Description', widget=MarkItUpWidget())
    kind = forms.CharField(
        widget=AutocompleteWithFavorites(ResourceKind,
            '/resource/search_by_kind/',
            ResourceKind.objects.all()[:10]))
    tags = forms.Field(
        widget=TaggitWidget(autocomplete_url="/resource/search_by_tag/"),
        required=False)
    community = forms.CharField(
        widget=Autocomplete(Community, '/community/search_by_name'))
    geometry = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Resource
        fields = ['name', 'description', 'kind', 'tags', 'community', 'id',
                  'geometry']

    _field_labels = {
        'name': _('Name'),
        'description': _('Description'),
        'kind': _('Kind'),
        'tags': _('Tags'),
        'community': _('Community')
    }

    def __init__(self, *args, **kwargs):
        # Crispy forms configuration
        self.helper = MooHelper()
        self.helper.form_id = 'form_resource'

        r = super(FormResource, self).__init__(*args, **kwargs)

        for field, label in self._field_labels.iteritems():
            self.fields[field].label = label

        return r

    def save(self, user=None, *args, **kwargs):
        resource = super(FormResource, self).save(*args, **kwargs)
        if user and not user.is_anonymous():
            resource.creator_id = user.id
            resource.save()
        return resource

    def clean_kind(self):
        return ResourceKind.objects.get(id=self.cleaned_data['kind'])

    def clean_community(self):
        return Community.objects.get(id=self.cleaned_data['community'])
