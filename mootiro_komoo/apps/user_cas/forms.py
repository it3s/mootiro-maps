# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from ajaxforms import AjaxModelForm
from main.utils import MooHelper


class FormProfile(AjaxModelForm):

    class Meta:
        model = User
        fields = ['username', ]

    def __init__(self, *a, **kw):
        self.helper = MooHelper(form_id="profile-form")
        self.helper.form_action = reverse('profile_update')
        return super(FormProfile, self).__init__(*a, **kw)
