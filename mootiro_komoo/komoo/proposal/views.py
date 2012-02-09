#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from annoying.decorators import render_to
from ..need.models import Need
from .models import Proposal
from .forms import ProposalForm


def view(request, need_slug, id):
    proposal = Proposal.objects.get(id=id)
    return render_to_response('proposal_view.html', dict(proposal=proposal))


@render_to('proposal_edit.html')
def new(request, need_slug):
    return dict(form=ProposalForm(),
                action=reverse('save_proposal', args=(need_slug,)))


@render_to('proposal_edit.html')
def save(request, need_slug):
    need = Need.objects.get(slug=need_slug)
    proposal = Proposal(need=need)
    form = ProposalForm(request.POST, instance=proposal)
    if form.is_valid():
        proposal = form.save()
        return redirect(view, need_slug, proposal.id)
    else:
        return dict(form=form)


@render_to('proposal_edit.html')
def edit(request, need_slug, id):
    p = Proposal.objects.get(id=id)
    return dict(form=ProposalForm(instance=p),
                action=reverse('save_proposal', args=(need_slug,)))
