#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.forms import CharField
from django.utils.translation import ugettext_lazy as _
from annoying.decorators import autostrip
from markitup.widgets import MarkItUpWidget
from ajaxforms import AjaxModelForm

from main.utils import MooHelper
from proposal.models import Proposal
from signatures.signals import notify_on_update


@autostrip
class ProposalForm(AjaxModelForm):
    description = CharField(widget=MarkItUpWidget())

    class Meta:
        model = Proposal
        fields = ('title', 'description', 'cost')

    _field_labels = {
        'title': _('Title'),
        'description': _('Description'),
        'cost': _('Cost'),
    }

    def __init__(self, *a, **kw):
        # Crispy forms configuration
        self.helper = MooHelper(form_id="proposal_form")
        return super(ProposalForm, self).__init__(*a, **kw)

    @notify_on_update
    def save(self, *a, **kw):
        return super(ProposalForm, self).save(*a, **kw)
