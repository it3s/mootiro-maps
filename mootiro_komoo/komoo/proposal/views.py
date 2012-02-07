#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from ..need.models import Need
from .models import Proposal
from .forms import ProposalForm


def view(request, id):
    proposal = Proposal.objects.get(id=id)
    return render_to_response('proposal_view.html', dict(proposal=proposal))


def new(request, community_slug, need_slug):
    return render_to_response('proposal_edit.html',
            dict(form=ProposalForm(),
                 action=reverse('save_proposal',
                                args=(community_slug, need_slug))),
            context_instance=RequestContext(request))


def save(request, community_slug, need_slug):
    need = Need.objects.get(slug=need_slug)
    proposal = Proposal(need=need)
    form = ProposalForm(request.POST, instance=proposal)
    if form.is_valid():
        proposal = form.save()
        # return redirect('komoo.proposal.views.view', proposal.id)
        # return redirect('view_proposal', proposal.id)
        return redirect(view, proposal.id)
    else:
        return render_to_response('proposal_edit.html', dict(form=form),
            context_instance=RequestContext(request))


def edit(request, id):
    p = Proposal.objects.get(id=id)
    context = dict(form=ProposalForm(instance=p))
    return render_to_response('proposal_edit.html', context,
            context_instance=RequestContext(request))
