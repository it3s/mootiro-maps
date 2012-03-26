# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.db.models.query_utils import Q

from markitup.widgets import MarkItUpWidget
from ajax_select.fields import AutoCompleteSelectMultipleField

from main.utils import MooHelper
# from main.widgets import Autocomplete
from community.models import Community
from organization.models import Organization


class FormOrganization(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    description = forms.CharField('Description', required=False,
        widget=MarkItUpWidget())
    community = AutoCompleteSelectMultipleField('community', required=False)
    # geometry = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Organization
        fields = ['name', 'description', 'community', 'id',]# 'geometry']

    _field_labels = {
        'name': _('Name'),
        'description': _('Description'),
        'community': _('Community')
    }

    def __init__(self, *args, **kwargs):
        self.helper = MooHelper()
        self.helper.form_id = 'form_organization'

        org = super(FormOrganization, self).__init__(*args, **kwargs)

        # TODO make this generic and work for any AutoCompleteSelectMultipleField
        my_args = args[0] if args and len(args) > 0 else None
        if my_args and 'community_text' in my_args:
            community_text = my_args.get('community_text', '')
            q = Community.objects.filter(Q(name__iexact=community_text) |
                Q(slug__iexact=community_text))
            if not q.count():
                Community(name=community_text).save()

        for field, label in self._field_labels.iteritems():
            self.fields[field].label = label

        return org

    def save(self, user=None, *args, **kwargs):
        org = super(FormOrganization, self).save(*args, **kwargs)
        if user and not user.is_anonymous():
            org.creator_id = user.id
            org.save()
        return org

    # def clean_community(self):
    #     if self.cleaned_data.get('community', None):
    #         return Community.objects.get(id=self.cleaned_data['community'])
    #     else:
    #         return []
