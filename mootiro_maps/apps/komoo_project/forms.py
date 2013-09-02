# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from markitup.widgets import MarkItUpWidget
from fileupload.forms import FileuploadField, SingleFileUploadWidget
from fileupload.models import UploadedFile
from ajax_select.fields import AutoCompleteSelectMultipleField
from ajaxforms import AjaxModelForm
from django.template.defaultfilters import slugify
from django.db.models.query_utils import Q
from main.utils import MooHelper, clean_autocomplete_field
from main.widgets import TaggitWidget
from .models import Project

logger = logging.getLogger(__name__)


PUBLIC_CHOICES = (
        ('publ', _('Public')),
        ('priv', _('Private'))
)


class FormProject(AjaxModelForm):
    description = forms.CharField(widget=MarkItUpWidget())
    contact = forms.CharField(required=False, widget=MarkItUpWidget())
    tags = forms.Field(required=False, widget=TaggitWidget(
        autocomplete_url="/project/search_tags/"))
    logo = FileuploadField(required=False, widget=SingleFileUploadWidget)
    partners_logo = FileuploadField(required=False)

    class Meta:
        model = Project
        fields = ('name', 'short_description', 'description', 'tags',
                    'contact', 'logo', 'id')

    _field_labels = {
        'name': _('Name'),
        'short_description': _('Short description'),
        'description': _('Description'),
        'tags': _('Tags'),
        'logo': _('Logo'),
        'contact': _('Contact'),
        'partners_logo': _('Partners Logo'),
    }

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id='form_project')
        return super(FormProject, self).__init__(*a, **kw)

    def save(self, *a, **kw):
        proj = super(FormProject, self).save(*a, **kw)
        UploadedFile.bind_files(
                self.cleaned_data.get('partners_logo', '').split('|'), proj)
        return proj

    def clean_logo(self):
        return clean_autocomplete_field(self.cleaned_data['logo'],
                                        UploadedFile)

    def clean(self):
        super(FormProject, self).clean()
        try:
            if not self.cleaned_data['id']:
                self.validation('name',
                    u'O sistema já possui um projeto com este nome',
                    Project.objects.filter(
                        Q(name__iexact=self.cleaned_data['name']) |
                        Q(slug=slugify(self.cleaned_data['name']))
                    ).count())
        except Exception as err:
            logger.error('Validation Error: {}'.format(err))
        finally:
            return self.cleaned_data
