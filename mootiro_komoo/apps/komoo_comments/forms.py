#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django import forms
from django.forms import fields

from komoo_comments.models import Comment


class FormComment(forms.ModelForm):
    parent_id = fields.CharField(required=False, widget=fields.HiddenInput())
    content_type_id = fields.CharField(required=False, widget=fields.HiddenInput())
    object_id = fields.CharField(required=False, widget=fields.HiddenInput())

    class Meta:
        model = Comment
        fields = ['comment', 'content_type_id', 'object_id']
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 80, 'rows': 5, 'class': 'span8'}),
        }

    def save(self, user=None, *args, **kwargs):
        comment = super(FormComment, self).save(*args, **kwargs)
        update = False
        if user and not user.is_anonymous():
            print 'USER: %s' % user
            comment.author_id = user.id
            update = True
        if self.cleaned_data.get('content_type_id', None):
            comment.content_type_id = self.cleaned_data['content_type_id']
            update = True
        if self.cleaned_data['parent_id']:
            comment.parent = Comment.objects.get(pk=self.cleaned_data['parent_id'])
            update = True
        if update:
            comment.save()
        return comment
