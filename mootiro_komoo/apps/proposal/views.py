#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from annoying.decorators import render_to
from ajaxforms import ajax_form

from community.models import Community
from need.models import Need
from proposal.models import Proposal
from proposal.forms import ProposalForm

logger = logging.getLogger(__name__)


def prepare_proposal_objects(community_slug="", need_slug="", proposal_number=""):
    """Retrieves a tuple (proposal, need, community). According to given
    parameters may raise an 404. Creates a new proposal if proposal_number is
    evaluated as false."""
    community = get_object_or_404(Community, slug=community_slug) \
                    if community_slug else None

    filters = dict(slug=need_slug)
    if community_slug:
        filters["community"] = community
    need = get_object_or_404(Need, **filters)

    if proposal_number:
        proposal = get_object_or_404(Proposal, number=proposal_number, need=need)
    else:
        proposal = Proposal(need=need)

    return proposal, need, community


@login_required
@ajax_form('proposal/edit.html', ProposalForm)
def edit(request, community_slug="", need_slug="", proposal_number=""):
    logger.debug('acessing proposal > edit')
    proposal, need, community = prepare_proposal_objects(community_slug,
        need_slug, proposal_number)

    def on_get(request, form):
        return ProposalForm(instance=proposal)

    def on_before_validation(request, form):
        if form.instance:
            form.instance.need = proposal.need
            if proposal.number:
                form.instance.number = proposal.number
        return form

    def on_after_save(request, proposal):
        kw = dict(need_slug=proposal.need.slug, proposal_number=proposal.number)
        if proposal.need.community.count():
            kw["community_slug"] = proposal.need.community.all()[0].slug
        return {'redirect': reverse('view_proposal', kwargs=kw)}

    return {'on_get': on_get, 'on_before_validation': on_before_validation,
            'on_after_save': on_after_save, 'community': community,
            'need': need}


@render_to('proposal/view.html')
def view(request, community_slug="", need_slug="", proposal_number=""):
    logger.debug('accessing proposal > view')

    proposal, need, community = prepare_proposal_objects(community_slug,
        need_slug, proposal_number)
    return dict(proposal=proposal, community=community)
