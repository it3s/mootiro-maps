# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from ajaxforms import AjaxModelForm
from markitup.widgets import MarkItUpWidget
from main.utils import MooHelper


class FormProfile(AjaxModelForm):
    contact = forms.CharField(required=False, widget=MarkItUpWidget())
    # geometry = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta():
        fields = ['contact', 'id']

    _field_labels = {
        'contact': _('Public Contact')
    }

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id='form-profile')
        return super(FormProfile, self).__init__(*a, **kw)

