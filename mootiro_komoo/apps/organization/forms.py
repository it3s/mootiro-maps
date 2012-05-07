# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.forms import ValidationError

from markitup.widgets import MarkItUpWidget
from ajax_select.fields import AutoCompleteSelectMultipleField

from crispy_forms.helper import FormHelper
from main.utils import MooHelper
from main.widgets import Tagsinput, TaggitWidget
from organization.models import (Organization, OrganizationBranch,
                OrganizationCategory, OrganizationCategoryTranslation)
from need.models import TargetAudience
from fileupload.forms import FileuploadField
from fileupload.models import UploadedFile

if settings.LANGUAGE_CODE == 'en-us':
    CATEGORIES = [(cat.id, cat.name) \
                    for cat in OrganizationCategory.objects.all()]
else:
    CATEGORIES = [(cat.category_id, cat.name)\
                    for cat in OrganizationCategoryTranslation.objects.filter(
                        lang=settings.LANGUAGE_CODE)]


class FormOrganizationNew(forms.ModelForm):
    description = forms.CharField(required=False, widget=MarkItUpWidget())
    community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)
    contact = forms.CharField(required=False, widget=MarkItUpWidget())
    target_audiences = forms.Field(required=False,
        widget=Tagsinput(
            TargetAudience,
            autocomplete_url="/need/target_audience_search")
    )
    # categories = AutoCompleteSelectMultipleField('organizationcategory',
    #     help_text='', required=False)
    categories = forms.MultipleChoiceField(required=False, choices=CATEGORIES,
        widget=forms.CheckboxSelectMultiple(
                    attrs={'class': 'org-widget-categories'}))
    files = FileuploadField(required=False)
    logo = forms.CharField(required=False, widget=forms.HiddenInput())
    tags = forms.Field(
        widget=TaggitWidget(autocomplete_url="/organization/search_by_tag/"),
        required=False)

    class Meta:
        model = Organization
        fields = ['description', 'community', 'link', 'contact',
        'target_audiences', 'categories', 'tags', 'files',  'logo']

    _field_labels = {
        'description': _('Description'),
        'community': _('Community'),
        'contact': _('Contact'),
        'tags': _('Tags'),
        'target_audiences': _('Target Audience'),
        'categories': _('Categories'),
        'files': _(' '),
        'logo': _(' ')
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

    def clean(self, *a, **kw):
        r = super(FormOrganizationNew, self).clean(*a, **kw)
        if not self.org_name:
            self._errors['name'] = _('Name is required')
            raise ValidationError(_('Name is required'))
        elif Organization.objects.filter(name=self.org_name).count():
            self._errors['name'] = _('Name must be unique')
            raise ValidationError(_('Name must be unique'))
        return r

    def save(self, user=None, *args, **kwargs):
        org = Organization()
        org.description = self.cleaned_data['description']
        org.contact = self.cleaned_data['contact']
        org.link = self.cleaned_data['link']
        org.name = self.org_name
        org.logo = self.cleaned_data.get('logo', None)
        if user and not user.is_anonymous():
            org.creator_id = user.id
        org.save()

        for com in self.cleaned_data['community']:
            org.community.add(com)

        for target_aud in self.cleaned_data['target_audiences']:
            org.target_audiences.add(target_aud)

        for c in self.cleaned_data['categories']:
            org.categories.add(c)

        for t in self.cleaned_data['tags']:
            org.tags.add(t)

        files_id_list = self.cleaned_data.get('files', '').split('|')
        UploadedFile.bind_files(files_id_list, org)

        return org

    def clean_logo(self):
        try:
            if not self.cleaned_data['logo'] or self.cleaned_data['logo'] == 'None':
                return UploadedFile()
            else:
                return UploadedFile.objects.get(id=self.cleaned_data['logo'])
        except:
            raise forms.ValidationError(_('invalid logo data'))


class FormOrganizationEdit(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    description = forms.CharField(required=False, widget=MarkItUpWidget())
    community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)
    contact = forms.CharField(required=False, widget=MarkItUpWidget())
    target_audiences = forms.Field(required=False,
        widget=Tagsinput(
            TargetAudience,
            autocomplete_url="/need/target_audience_search")
    )
    # categories = AutoCompleteSelectMultipleField('organizationcategory',
    #     help_text='', required=False)
    categories = forms.MultipleChoiceField(required=False, choices=CATEGORIES,
        widget=forms.CheckboxSelectMultiple(
                    attrs={'class': 'org-widget-categories'}))
    files = FileuploadField(required=False)
    logo = forms.CharField(required=False, widget=forms.HiddenInput())
    tags = forms.Field(
        widget=TaggitWidget(autocomplete_url="/organization/search_by_tag/"),
        required=False)

    class Meta:
        model = Organization
        fields = ['name', 'description', 'community', 'link', 'contact',
                  'target_audiences', 'categories', 'tags', 'id', 'logo']

    _field_labels = {
        'name': _('Name'),
        'description': _('Description'),
        'community': _('Community'),
        'contact': _('Contact'),
        'tags': _('Tags'),
        'target_audiences': _('Target Audiences'),
        'categories': _('Categories'),
        'files': _(' '),
        'logo': _(' ')
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

        files_id_list = self.cleaned_data.get('files', '').split('|')
        UploadedFile.bind_files(files_id_list, org)

        return org

    def clean_logo(self):
        try:
            if not self.cleaned_data['logo'] or self.cleaned_data['logo'] == 'None':
                return UploadedFile()
            else:
                return UploadedFile.objects.get(id=self.cleaned_data['logo'])
        except:
            raise forms.ValidationError(_('invalid logo data'))


class FormBranchNew(forms.Form):
    branch_name = forms.CharField()
    geometry = forms.CharField(required=False, widget=forms.HiddenInput())
    branch_info = forms.CharField(required=False, widget=MarkItUpWidget())
    branch_community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)

    _field_labels = {
        'branch_name': _('Branch Name'),
        'branch_info': _('Info'),
        'branch_community': _('Community')
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
        for comm in self.cleaned_data.get('branch_community', []):
            branch.community.add(comm)
        return branch
