#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to

from community.models import Community
from need.models import Need
from proposal.models import Proposal
from proposal.forms import ProposalForm

logger = logging.getLogger(__name__)


@render_to('proposal/edit.html')
def edit(request, community_slug="", need_slug="", proposal_number=""):
    logger.debug('acessing proposal > edit')
    # always receives all identifiers or none of them
    community = get_object_or_404(Community, slug=community_slug)
    need = get_object_or_404(Need, slug=need_slug, community=community)

    if proposal_number:
        proposal = get_object_or_404(Proposal, number=proposal_number)
    else:
        proposal = Proposal(need=need)
    if request.POST:
        form = ProposalForm(request.POST, instance=proposal)
        if form.is_valid():
            need = form.save()
            return redirect('view_proposal',
                    community_slug=proposal.need.community.slug,
                    need_slug=need.slug, proposal_number=proposal.number)
        else:
            return {'form': form}
    else:
        return {'form': ProposalForm(instance=proposal)}


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


#@render_to('proposal/proposal_edit.html')
#@login_required
#def edit0(request, need_slug, id):
#    logger.debug('accessing proposal > edit')
#    p = Proposal.objects.get(id=id)
#    return dict(form=ProposalForm(instance=p), action=reverse('save_proposal', args=(need_slug,)))
