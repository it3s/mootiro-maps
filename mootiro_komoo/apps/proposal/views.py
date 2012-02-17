#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to

from need.models import Need
from proposal.models import Proposal
from proposal.forms import ProposalForm

logger = logging.getLogger(__name__)

@render_to('proposal_view.html')
def view(request, need_slug, id):
    logger.debug('accessing proposal > view')

    proposal = Proposal.objects.get(id=id)
    return dict(proposal=proposal)


@render_to('proposal/proposal_edit.html')
@login_required
def new(request, need_slug):
    logger.debug('accessing proposal > new')
    return dict(form=ProposalForm(),
                action=reverse('save_proposal', args=(need_slug,)))


@render_to('proposal/proposal_edit.html')
@login_required
def save(request, need_slug):
    logger.debug('accessing proposal > save')
    need = Need.objects.get(slug=need_slug)
    proposal = Proposal(need=need, creator=request.user)
    form = ProposalForm(request.POST, instance=proposal)
    if form.is_valid():
        proposal = form.save()
        return redirect(view, need_slug, proposal.id)
    else:
        logger.debug('invalid form : {}'.format(form.errors))
        return dict(form=form)


@render_to('proposal/proposal_edit.html')
@login_required
def edit(request, need_slug, id):
    logger.debug('accessing proposal > edit')
    p = Proposal.objects.get(id=id)
    return dict(form=ProposalForm(instance=p), action=reverse('save_proposal', args=(need_slug,)))
