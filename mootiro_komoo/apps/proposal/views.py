#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from annoying.decorators import render_to
from ajaxforms import ajax_form

from komoo_user.utils import login_required
from need.models import Need
from proposal.models import Proposal
from proposal.forms import ProposalForm

logger = logging.getLogger(__name__)


def prepare_proposal_objects(need_id='', proposal_id=''):
    """
    Retrieves a tuple (proposal, need). According to given
    parameters may raise an 404. Creates a new proposal if proposal_id is
    evaluated as false.
    """
    need = get_object_or_404(Need, pk=need_id) if need_id else None

    if proposal_id:
        proposal = get_object_or_404(Proposal, pk=proposal_id)
    elif need:
        proposal = Proposal(need=need)
    else:
        proposal = Proposal()
    return proposal, need


@login_required
@ajax_form('proposal/edit.html', ProposalForm)
def edit(request, id=""):
    need_id = request.GET.get('need', '')
    proposal, need = prepare_proposal_objects(need_id, id)

    def on_get(request, form):
        return ProposalForm(instance=proposal)

    def on_after_save(request, obj):
        return {'redirect': reverse('view_proposal', kwargs={'id': obj.id})}

    return {'on_get': on_get, 'on_after_save': on_after_save, 'need': need}


@render_to('proposal/view.html')
def view(request, id=""):
    proposal = get_object_or_404(Proposal, pk=id)
    return {'proposal': proposal}
