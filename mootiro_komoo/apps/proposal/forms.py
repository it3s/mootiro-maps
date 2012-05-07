#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.forms import ModelForm, CharField
from django.utils.translation import ugettext_lazy as _
from annoying.decorators import autostrip
from markitup.widgets import MarkItUpWidget

from main.utils import MooHelper
from proposal.models import Proposal


@autostrip
class ProposalForm(ModelForm):
    '''https://github.com/aljosa/django-tinymce/blob/master/docs/usage.rst'''

    class Meta:
        model = Proposal
        fields = ('title', 'description', 'cost')

    _field_labels = {
        'title': _('Title'),
        'description': _('Description'),
        'cost': _('Cost'),
    }

    description = CharField(widget=MarkItUpWidget())

    def __init__(self, *a, **kw):
        # Crispy forms configuration
        self.helper = MooHelper()
        self.helper.form_id = "proposal_form"

        prop = super(ProposalForm, self).__init__(*a, **kw)
        for field, label in self._field_labels.iteritems():
            self.fields[field].label = label
        return prop
