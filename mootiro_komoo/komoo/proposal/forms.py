#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.forms import ModelForm, CharField
from annoying.decorators import autostrip
from tinymce.widgets import TinyMCE
from .models import Proposal


@autostrip
class ProposalForm(ModelForm):
    '''https://github.com/aljosa/django-tinymce/blob/master/docs/usage.rst'''
    # content = CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    content = CharField(widget=TinyMCE())
    # report = CharField(widget=TinyMCE(), required=False)

    class Meta:
        model = Proposal
        exclude = 'report creator'.split()
