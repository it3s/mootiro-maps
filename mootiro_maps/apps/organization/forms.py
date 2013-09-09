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
from annoying.functions import get_object_or_None

from main.utils import MooHelper, clean_autocomplete_field
from main.widgets import Tagsinput, TaggitWidget
from organization.models import (Organization, OrganizationCategory,
        OrganizationCategoryTranslation)
from komoo_project.models import Project
from need.models import TargetAudience
from fileupload.forms import FileuploadField, LogoField
from fileupload.models import UploadedFile
from ajaxforms import AjaxModelForm
from signatures.signals import notify_on_update

if settings.LANGUAGE_CODE == 'en-us':
    CATEGORIES = [(cat.id, cat.name)
                for cat in OrganizationCategory.objects.all().order_by('name')]
else:
    CATEGORIES = [(cat.category_id, cat.name)
                    for cat in OrganizationCategoryTranslation.objects.filter(
                        lang=settings.LANGUAGE_CODE).order_by('name')]


logger = logging.getLogger(__name__)


class FormOrganization(AjaxModelForm):
    class Meta:
        model = Organization
        fields = ('name', 'short_description', 'description', 'community',
                  'link', 'contact', 'target_audiences', 'categories', 'tags',
                  'id', 'logo', 'logo_category', 'logo_choice', 'project_id')

    _field_labels = {
        'name': _('Name'),
        'short_description': _('Short description'),
        'description': _('Description'),
        'community': _('Community'),
        'contact': _('Contact'),
        'tags': _('Tags'),
        'target_audiences': _('Target Audiences'),
        'categories': _('Categories'),
        'files': _('Images'),
        'logo': _('Logo')
    }

    description = forms.CharField(required=False, widget=MarkItUpWidget())
    community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)
    contact = forms.CharField(required=False, widget=MarkItUpWidget())
    target_audiences = forms.Field(required=False,
        widget=Tagsinput(
            TargetAudience,
            autocomplete_url="/need/target_audience_search"))
    categories = forms.MultipleChoiceField(required=False, choices=CATEGORIES,
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'org-widget-categories'}))
    files = FileuploadField(required=False)
    logo = LogoField(required=False)
    logo_choice = forms.CharField(required=False, widget=forms.HiddenInput())
    logo_category = forms.CharField(required=False, widget=forms.HiddenInput())
    tags = forms.Field(
        widget=TaggitWidget(autocomplete_url="/organization/search_tags/"),
        required=False)
    project_id = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        self.helper = MooHelper(form_id='form_organization')
        return super(FormOrganization, self).__init__(*args, **kwargs)

    def clean(self):
        super(FormOrganization, self).clean()
        try:
            self.validation('name',
                    u'O sistema já possui uma organização com este nome',
                    Organization.objects.filter((
                        Q(name__iexact=self.cleaned_data['name']) |
                        Q(slug=slugify(self.cleaned_data['name']))) &
                        ~Q(pk=self.cleaned_data['id'])
                    ).count())
        except Exception as err:
            logger.error('Validation Error: {}'.format(err))
        finally:
            return self.cleaned_data

    @notify_on_update
    def save(self, *args, **kwargs):
        org = super(FormOrganization, self).save(*args, **kwargs)
        UploadedFile.bind_files(
            self.cleaned_data.get('files', '').split('|'), org)

        # Add the community to project if a project id was given.
        project_id = self.cleaned_data.get('project_id', None)
        if project_id:
            project = get_object_or_None(Project, pk=int(project_id))
            if project:
                project.save_related_object(org, self.user)

        return org

    def clean_logo(self):
        return clean_autocomplete_field(self.cleaned_data['logo'],
                                        UploadedFile)

    def clean_logo_category(self):
        return clean_autocomplete_field(self.cleaned_data['logo_category'],
                                        OrganizationCategory)


class FormOrganizationGeoRef(FormOrganization):
    geometry = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Organization
        fields = ('name', 'short_description', 'description', 'community',
                  'link', 'contact', 'target_audiences', 'categories', 'tags',
                  'id', 'logo', 'logo_category', 'logo_choice', 'geometry',
                  'project_id')
