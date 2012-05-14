# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.template.defaultfilters import slugify
from django.db.models.query_utils import Q

from markitup.widgets import MarkItUpWidget
from ajax_select.fields import AutoCompleteSelectMultipleField

from crispy_forms.helper import FormHelper
from main.utils import MooHelper, clean_autocomplete_field
from main.widgets import Tagsinput, TaggitWidget
from organization.models import (Organization, OrganizationBranch,
                OrganizationCategory, OrganizationCategoryTranslation)
from need.models import TargetAudience
from fileupload.forms import FileuploadField
from fileupload.models import UploadedFile
from ajaxforms import AjaxModelForm

if settings.LANGUAGE_CODE == 'en-us':
    CATEGORIES = [(cat.id, cat.name) \
                    for cat in OrganizationCategory.objects.all()]
else:
    CATEGORIES = [(cat.category_id, cat.name)\
                    for cat in OrganizationCategoryTranslation.objects.filter(
                        lang=settings.LANGUAGE_CODE)]


logger = logging.getLogger(__name__)


class FormOrganization(AjaxModelForm):
    description = forms.CharField(required=False, widget=MarkItUpWidget())
    community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)
    contact = forms.CharField(required=False, widget=MarkItUpWidget())
    target_audiences = forms.Field(required=False,
        widget=Tagsinput(
            TargetAudience,
            autocomplete_url="/need/target_audience_search")
    )
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
        self.helper = MooHelper(form_id='form_organization')
        return super(FormOrganization, self).__init__(*args, **kwargs)

    def clean(self):
        super(FormOrganization, self).clean()
        try:
            if not self.cleaned_data['id']:
                self.validation('name',
                    u'O sistema já possui uma organização com este nome',
                    Organization.objects.filter(
                        Q(name__iexact=self.cleaned_data['name']) | \
                        Q(slug=slugify(self.cleaned_data['name']))
                    ).count()
                )
        except Exception as err:
            logger.error('Validation Error: {}'.format(err))
        finally:
            return self.cleaned_data

    def save(self, *args, **kwargs):
        org = super(FormOrganization, self).save(*args, **kwargs)
        UploadedFile.bind_files(
            self.cleaned_data.get('files', '').split('|'), org)
        return org

    def clean_logo(self):
        return clean_autocomplete_field(self.cleaned_data['logo'], UploadedFile)


class FormBranch(AjaxModelForm):
    name = forms.CharField()
    geometry = forms.CharField(required=False, widget=forms.HiddenInput())
    info = forms.CharField(required=False, widget=MarkItUpWidget())
    community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)
    organization = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = OrganizationBranch
        fields = ['id', 'name',
            # 'geometry',
            'info', 'community', 'organization']

    _field_labels = {
        'name': _('Branch Name'),
        'info': _('Info'),
        'community': _('Community'),
        'organization': _(' ')
    }

    def __init__(self, *args, **kwargs):
        self.helper = MooHelper(form_id='form_branch')
        return super(FormBranch, self).__init__(*args, **kwargs)

    def clean_organization(self):
        return clean_autocomplete_field(
            self.cleaned_data['organization'], Organization)
