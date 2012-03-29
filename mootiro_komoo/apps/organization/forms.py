# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from markitup.widgets import MarkItUpWidget
from ajax_select.fields import AutoCompleteSelectMultipleField

from crispy_forms.helper import FormHelper
from organization.models import Organization, OrganizationBranch
from community.models import Community


class FormOrganization(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    description = forms.CharField(required=False, widget=MarkItUpWidget())
    community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)
    contact = forms.CharField(required=False, widget=MarkItUpWidget())

    class Meta:
        model = Organization
        fields = ['description', 'community', 'link', 'contact', 'id']

    _field_labels = {
        # 'name': _('Name'),
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

        org = super(FormOrganization, self).__init__(*args, **kwargs)

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


class FormBranch(forms.Form):
    branch_geometry = forms.CharField(required=False, widget=forms.HiddenInput())
    branch_description = forms.CharField(required=False, widget=MarkItUpWidget())
    branch_contact = forms.CharField(required=False, widget=MarkItUpWidget())

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False

        return super(FormBranch, self).__init__(*args, **kwargs)

    def save(self, user=None, organization=None, *args, **kwargs):
        branch = OrganizationBranch()
        if 'branch_geometry' in self.fields:
            branch.geometry = self.cleaned_data.get('branch_geometry', '')
        branch.description = self.cleaned_data.get('branch_description', None)
        branch.contact = self.cleaned_data.get('branch_contact', None)
        if user and not user.is_anonymous():
            branch.creator_id = user.id
        branch.organization = organization
        branch.save()
        return branch
