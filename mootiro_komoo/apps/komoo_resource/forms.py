# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import traceback
import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from markitup.widgets import MarkItUpWidget
from fileupload.forms import FileuploadField
from fileupload.models import UploadedFile
from ajaxforms import AjaxModelForm

from main.utils import MooHelper, clean_autocomplete_field
from main.widgets import Autocomplete, TaggitWidget, AutocompleteWithFavorites
from komoo_resource.models import Resource, ResourceKind
from community.models import Community

logger = logging.getLogger(__name__)


class FormResource(AjaxModelForm):
    description = forms.CharField(
        widget=MarkItUpWidget()
    )
    kind = forms.CharField(required=False,
        widget=AutocompleteWithFavorites(ResourceKind,
                    '/resource/search_by_kind/',
                     ResourceKind.favorites(number=10), can_add=True)
    )
    tags = forms.Field(required=False,
        widget=TaggitWidget(autocomplete_url="/resource/search_by_tag/")
    )
    community = forms.CharField(required=False,
        widget=Autocomplete(Community, '/community/search_by_name')
    )
    # geometry = forms.CharField(required=False,
    #     widget=forms.HiddenInput()
    # )
    # files = FileuploadField(required=False)

    class Meta:
        model = Resource
        fields = (
            'name', 'description', 'kind', 'tags', 'community', 'id',
            # 'geometry', 'files'
        )

    _field_labels = {
        'name': _('Name'),
        'description': _('Description'),
        'kind': _('Kind'),
        'tags': _('Tags'),
        'community': _('Community'),
        # 'files': ''
    }

    def __init__(self, *args, **kwargs):
        self.helper = MooHelper(form_id='form_resource')
        self.helper.form_action = '/resource/new_resource/'
        return super(FormResource, self).__init__(*args, **kwargs)

    def clean(self):
        super(FormResource, self).clean()
        try:
            self.validation('description', u'BLA',
                            True)
        except Exception as err:
            logger.error('Erro de validacao: {}\n{}'.format(err,
                traceback.format_exc()))
        finally:
            return self.cleaned_data

    def save(self, user=None, *args, **kwargs):
        resource = super(FormResource, self).save(*args, **kwargs)
        if user and not user.is_anonymous():
            resource.creator_id = user.id
            resource.save()

        files_id_list = self.cleaned_data.get('files', '').split('|')
        UploadedFile.bind_files(files_id_list, resource)

        return resource

    def clean_kind(self):
        return clean_autocomplete_field(self.cleaned_data['kind'], ResourceKind)

    def clean_community(self):
        return clean_autocomplete_field(self.cleaned_data['community'], Community)
