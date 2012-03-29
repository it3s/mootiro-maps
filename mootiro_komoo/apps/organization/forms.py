# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from markitup.widgets import MarkItUpWidget
from ajax_select.fields import AutoCompleteSelectMultipleField

from crispy_forms.helper import FormHelper
from main.utils import MooHelper
from organization.models import Organization, OrganizationBranch
from community.models import Community


class FormOrganizationNew(forms.ModelForm):
    description = forms.CharField(required=False, widget=MarkItUpWidget())
    community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)
    contact = forms.CharField(required=False, widget=MarkItUpWidget())

    class Meta:
        model = Organization
        fields = ['description', 'community', 'link', 'contact']

    _field_labels = {
        'description': _('Description'),
        'community': _('Community'),
        'contact': _('Contact'),
    }

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False

        post = args[0] if args and len(args) > 0 else None
        if post:
            self.org_name = post.get('org_name_text')

        org = super(FormOrganizationNew, self).__init__(*args, **kwargs)

        for field, label in self._field_labels.iteritems():
            self.fields[field].label = label

        return org

    def save(self, user=None, *args, **kwargs):
        org = Organization()
        org.description = self.cleaned_data['description']
        org.contact = self.cleaned_data['contact']
        org.link = self.cleaned_data['link']
        org.name = self.org_name
        if user and not user.is_anonymous():
            org.creator_id = user.id
        org.save()
        for com in self.cleaned_data['community']:
            org.community.add(Community.objects.get(pk=com))

        return org


class FormOrganizationEdit(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    description = forms.CharField(required=False, widget=MarkItUpWidget())
    community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)
    contact = forms.CharField(required=False, widget=MarkItUpWidget())

    class Meta:
        model = Organization
        fields = ['name', 'description', 'community', 'link', 'contact', 'id']

    _field_labels = {
        'name': _('Name'),
        'description': _('Description'),
        'community': _('Community'),
        'contact': _('Contact'),
    }

    def __init__(self, *args, **kwargs):
        self.helper = MooHelper()
        self.helper.form_id = 'form_organization'

        org = super(FormOrganizationEdit, self).__init__(*args, **kwargs)
        for field, label in self._field_labels.iteritems():
            self.fields[field].label = label

        return org

    def save(self, user=None, *args, **kwargs):
        org = super(FormOrganizationEdit, self).save(*args, **kwargs)

        if user and not user.is_anonymous():
            org.creator_id = user.id
            org.save()
        return org


class FormBranchNew(forms.Form):
    branch_name = forms.CharField()
    geometry = forms.CharField(required=False, widget=forms.HiddenInput())
    branch_info = forms.CharField(required=False, widget=MarkItUpWidget())

    _field_labels = {
        'branch_name': _('Branch Name'),
        'branch_info': _('Info'),
    }

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False

        b = super(FormBranchNew, self).__init__(*args, **kwargs)

        for field, label in self._field_labels.iteritems():
            self.fields[field].label = label

        return b

    def save(self, user=None, organization=None, *args, **kwargs):
        branch = OrganizationBranch()
        if 'geometry' in self.fields:
            branch.geometry = self.cleaned_data.get('geometry', '')
        branch.info = self.cleaned_data.get('branch_info', None)
        branch.name = self.cleaned_data.get('branch_name', None)
        if user and not user.is_anonymous():
            branch.creator_id = user.id
        branch.organization = organization
        branch.save()
        return branch
