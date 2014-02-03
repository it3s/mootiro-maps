# -*- coding: utf-8 -*-
import logging
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from ajaxforms import AjaxModelForm
from komoo_map.forms import MapButtonWidget
from fileupload.forms import FileuploadField
from fileupload.models import UploadedFile
from markitup.widgets import MarkItUpWidget
from main.utils import MooHelper
from main.widgets import ContactsWidget
from .models import User, SocialAuth

logger = logging.getLogger(__name__)


class FormProfile(AjaxModelForm):
    about_me = forms.CharField(required=False, widget=MarkItUpWidget())
    name = forms.CharField(required=False)
    geometry = forms.CharField(required=False, widget=MapButtonWidget)
    #geometry = forms.CharField(required=False, widget=forms.HiddenInput())
    contacts = forms.CharField(required=False, widget=ContactsWidget())
    photo = FileuploadField(required=False)

    class Meta:
        model = User
        fields = ['name', 'about_me', 'id', 'geometry', 'contacts']

    _field_labels = {
        'name': _('Full name'),
        'about_me': _('About me'),
        'photo': _('Photo'),
        'geometry': _('Location'),
        'contacts': _('Contacts'),
    }

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id='form-profile')
        self.helper.form_action = reverse('profile_update_public_settings')
        super(FormProfile, self).__init__(*a, **kw)
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
        'password_confirmation': _('Confirm your password'),
    }

    name = forms.CharField(required=True)
    email = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput(
                attrs={'autocomplete': 'off'}))
    password_confirmation = forms.CharField(required=True,
                widget=forms.PasswordInput(attrs={'autocomplete': 'off'}))

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id="form_user")
        return super(FormUser, self).__init__(*a, **kw)

    def clean(self):
        """Form validations."""
        super(FormUser, self).clean()
        try:
            email = self.cleaned_data['email']

            if email:
                email = email.lower()
                self.cleaned_data['email'] = email

                self.validation('email', _('This email is already in use'),
                        User.objects.filter(email=email).exists())
                self.validation('email',
                    _('This email is registered on our system. You might have '
                      'logged before with a social account (Facebook or Google). '
                      'Please, skip this step and just login.'),
                    SocialAuth.objects.filter(email=email).exists())

            self.validation('password_confirmation',
                    _('Passwords did not match'),
                    self.cleaned_data['password'] !=
                    self.cleaned_data['password_confirmation'])
        except Exception as err:
            logger.error('Validation Error: {}'.format(err))
        finally:
            return self.cleaned_data

