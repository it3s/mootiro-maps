#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.forms import ModelForm, Form, CharField
from comments.models import Comment


class FormComment(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment', ]
