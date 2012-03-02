#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.forms import ModelForm, CharField
from annoying.decorators import autostrip
from tinymce.widgets import TinyMCE

from main.utils import MooHelper
from proposal.models import Proposal


@autostrip
class ProposalForm(ModelForm):
    '''https://github.com/aljosa/django-tinymce/blob/master/docs/usage.rst'''

    class Meta:
        model = Proposal
        exclude = 'report creator realizers need'.split()

    description = CharField(widget=TinyMCE())
    report = CharField(widget=TinyMCE(), required=False)

    def __init__(self, *a, **kw):
        # Crispy forms configuration
        self.helper = MooHelper()
        self.helper.form_id = "need_form"

        super(ProposalForm, self).__init__(*a, **kw)
