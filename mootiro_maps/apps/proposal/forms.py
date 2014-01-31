#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.forms import CharField, HiddenInput, Field
from django.utils.translation import ugettext_lazy as _
from annoying.decorators import autostrip
from markitup.widgets import MarkItUpWidget
from ajaxforms import AjaxModelForm

from main.utils import MooHelper, clean_autocomplete_field
from main.widgets import TaggitWidget, ContactsWidget
from proposal.models import Proposal
from need.models import Need
from signatures.signals import notify_on_update


@autostrip
class ProposalForm(AjaxModelForm):
    description = CharField(widget=MarkItUpWidget())
    need = CharField(widget=HiddenInput())
    contacts = CharField(required=False, widget=ContactsWidget())
    tags = Field(
        widget=TaggitWidget(autocomplete_url="/proposal/search_tags/"),
        required=False)

    class Meta:
        model = Proposal
        fields = ('title', 'short_description', 'description', 'contacts',
                  'cost', 'need', 'tags')

    _field_labels = {
        'title': _('Title'),
        'description': _('Description'),
        'short_description': _('Short description'),
        'contacts': _('Contacts'),
        'tags': _('Tags'),
        'cost': _('Cost'),
        'need': ' '
    }

    def __init__(self, *a, **kw):
        # Crispy forms configuration
        self.helper = MooHelper(form_id="proposal_form")
        return super(ProposalForm, self).__init__(*a, **kw)

    @notify_on_update
    def save(self, *a, **kw):
        return super(ProposalForm, self).save(*a, **kw)

    def clean_need(self):
        return clean_autocomplete_field(
            self.cleaned_data['need'], Need)
