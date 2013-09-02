#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django import forms
from django.forms import fields

from moderation.models import Moderation


class FormModeration(forms.ModelForm):
    content_type_id = fields.CharField(required=False, widget=fields.HiddenInput())
    object_id = fields.CharField(required=False, widget=fields.HiddenInput())

    class Meta:
        model = Moderation
        fields = ['comment', 'type_', 'content_type_id', 'object_id']
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 80, 'rows': 5, 'class': 'span8'}),
        }

    def save(self, user=None, *args, **kwargs):
        moderation = super(FormModeration, self).save(*args, **kwargs)
        update = False
        if user and not user.is_anonymous():
            moderation.author_id = user.id
            update = True
        if self.cleaned_data.get('content_type_id', None):
            moderation.content_type_id = self.cleaned_data['content_type_id']
            update = True
        if update:
            moderation.save()
        return moderation
