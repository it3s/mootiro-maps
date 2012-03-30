# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.db.models.query_utils import Q

from markitup.widgets import MarkItUpWidget
from fileupload.forms import FileuploadField

from main.utils import MooHelper
from main.widgets import Autocomplete, TaggitWidget, AutocompleteWithFavorites
from komoo_resource.models import Resource, ResourceKind
from community.models import Community
from fileupload.models import UploadedFile


class FormResource(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    description = forms.CharField('Description', widget=MarkItUpWidget())
    kind = forms.CharField(required=False,
        widget=AutocompleteWithFavorites(
            ResourceKind, '/resource/search_by_kind/',
            ResourceKind.favorites(number=10), can_add=True))
    tags = forms.Field(
        widget=TaggitWidget(autocomplete_url="/resource/search_by_tag/"),
        required=False)
    community = forms.CharField(required=False,
        widget=Autocomplete(Community, '/community/search_by_name'))
    files = FileuploadField(required=False)
    geometry = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Resource
        fields = ['name', 'description', 'kind', 'tags', 'community', 'id',
                  'geometry', 'files']

    _field_labels = {
        'name': _('Name'),
        'description': _('Description'),
        'kind': _('Kind'),
        'tags': _('Tags'),
        'community': _('Community'),
        'files': ''
    }

    def __init__(self, *args, **kwargs):
        # Crispy forms configuration
        self.helper = MooHelper()
        self.helper.form_id = 'form_resource'

        r = super(FormResource, self).__init__(*args, **kwargs)
        self.args = args[0] if args else {}

        for field, label in self._field_labels.iteritems():
            self.fields[field].label = label

        return r

    def save(self, user=None, *args, **kwargs):
        resource = super(FormResource, self).save(*args, **kwargs)
        if user and not user.is_anonymous():
            resource.creator_id = user.id
            resource.save()

        files_id_list = self.cleaned_data.get('files', '').split('|')
        UploadedFile.bind_files(files_id_list, resource)

        return resource

    def clean_kind(self):
        try:
            if self.cleaned_data['kind']:
                return ResourceKind.objects.get(id=self.cleaned_data['kind'])

            elif self.fields['kind'].widget.can_add and 'kind_autocomplete' in self.args:
                name = self.args['kind_autocomplete']
                if not ResourceKind.objects.filter(
                        Q(name__iexact=name) | Q(slug__iexact=name)).count():
                    rk = ResourceKind(name=name)
                    rk.save()
                return rk
        except Exception as err:
            print 'ERR: ', err
            raise forms.ValidationError(_('invalid kind data'))

    def clean_community(self):
        try:
            if not self.cleaned_data['community'] or self.cleaned_data['community'] == 'None':
                return Community()
            else:
                return Community.objects.get(id=self.cleaned_data['community'])
        except:
            raise forms.ValidationError(_('invalid community data'))
