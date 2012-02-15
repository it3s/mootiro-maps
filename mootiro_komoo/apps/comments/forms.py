#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.forms import ModelForm, Form, CharField
from comments.models import Comment
from django.forms import fields

class FormComment(ModelForm):
    parent_id = fields.CharField(required=False, widget=fields.HiddenInput())
    class Meta:
        model = Comment
        fields = ['comment',]

    # def __init__(self, *args, **kwargs):
    #     retorn = super(FormComment, self).__init__(*args, **kwargs)
    #     self.fields['parent'].widgets = fields.HiddenInput

    def save(self, *args, **kwargs):
        comment = super(FormComment, self).save(*args, **kwargs)
        if self.cleaned_data['parent_id']:
            comment.parent = Comment.objects.get(pk=self.cleaned_data['parent_id'])
            comment.save()
        return comment
