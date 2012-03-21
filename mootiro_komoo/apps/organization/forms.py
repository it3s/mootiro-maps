# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from markitup.widgets import MarkItUpWidget

from main.utils import MooHelper
from main.widgets import Autocomplete
from community.models import Community
from organization.models import Organization


class FormOrganization(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    description = forms.CharField('Description', widget=MarkItUpWidget())
    community = forms.CharField(
        widget=Autocomplete(Community, '/community/search_by_name'))
    geometry = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Organization
        fields = ['name', 'description', 'community', 'id', 'geometry']

    _field_labels = {
        'name': _('Name'),
        'description': _('Description'),
        'community': _('Community')
    }

    def __init__(self, *args, **kwargs):
        self.helper = MooHelper()
        self.helper.form_id = 'form_organization'

        org = super(FormOrganization, self).__init__(*args, **kwargs)

        for field, label in self._field_labels.iteritems():
            self.fields[field].label = label

        return org

    def save(self, user=None, *args, **kwargs):
        org = super(FormOrganization, self).save(*args, **kwargs)
        if user and not user.is_anonymous():
            org.creator_id = user.id
            org.save()
        return org

    def clean_community(self):
        return Community.objects.get(id=self.cleaned_data['community'])
