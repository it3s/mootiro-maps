#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.forms import ModelForm, Form, CharField, Textarea
from komoo_comments.models import Comment
from django.forms import fields

class FormComment(ModelForm):
    parent_id = fields.CharField(required=False, widget=fields.HiddenInput())
    class Meta:
        model = Comment
        fields = ['comment',]
        widgets = {
            'comment' : Textarea(attrs={'cols': 80, 'rows': 5, 'class' : 'span8'}),
        }

    def save(self, *args, **kwargs):
        comment = super(FormComment, self).save(*args, **kwargs)
        if self.cleaned_data['parent_id']:
            comment.parent = Comment.objects.get(pk=self.cleaned_data['parent_id'])
            comment.save()
        return comment
