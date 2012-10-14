# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from ajaxforms import AjaxModelForm
from komoo_map.forms import MapButtonWidget
from fileupload.forms import FileuploadField
from fileupload.models import UploadedFile
from markitup.widgets import MarkItUpWidget
from main.utils import MooHelper
from .models import User


class FormProfile(AjaxModelForm):
    contact = forms.CharField(required=False, widget=MarkItUpWidget())
    name = forms.CharField(required=False)
    geometry = forms.CharField(required=False, widget=MapButtonWidget)
    #geometry = forms.CharField(required=False, widget=forms.HiddenInput())
    photo = FileuploadField(required=False)

    class Meta:
        model = User
        fields = ['name', 'contact', 'id', 'geometry']

    _field_labels = {
        'name': _('Full Name'),
        'contact': _('Public Contact'),
        'photo': _('Photo'),
        'geometry': _('Location'),
    }

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id='form-profile')
        self.helper.form_action = reverse('profile_update_public_settings')
        r = super(FormProfile, self).__init__(*a, **kw)
        inst = kw.get('instance', None)
        if inst and not inst.name:
            self.fields['public_name'].initial = inst.user.name

    def save(self, *args, **kwargs):
        profile = super(FormProfile, self).save(*args, **kwargs)
        UploadedFile.bind_files(
            self.cleaned_data.get('photo', '').split('|'), profile)
        return profile


class FormUser(AjaxModelForm):
    '''Simplified use form with the minimun required info.'''

    class Meta:
        model = User
        fields = ('name', 'email', 'password')

    _field_labels = {
        'name': _('Name'),
        'email': _('Email'),
        'password': _('Password'),
    }

    name = forms.CharField(required=True)
    email = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id="form_user")
        return super(FormUser, self).__init__(*a, **kw)

    def clean(self):
        '''Form validations.'''
        super(FormUser, self).clean()
        email = self.cleaned_data['email']

        # TODO: if email is in use but was connected through external provider
        #       (facebook, google, etc...) show specific error.
        self.validation('email', _('This email is already in use.'),
                User.objects.filter(email=email).exists())

        return self.cleaned_data
