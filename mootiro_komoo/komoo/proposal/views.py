#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from ..need.models import Need
from .models import Proposal
from .forms import ProposalForm


def view(request, need_slug, id):
    proposal = Proposal.objects.get(id=id)
    return render_to_response('proposal_view.html', dict(proposal=proposal))


def new(request, need_slug):
    return render_to_response('proposal_edit.html',
            dict(form=ProposalForm(),
                 action=reverse('save_proposal', args=(need_slug,))),
            context_instance=RequestContext(request))


def save(request, need_slug):
    need = Need.objects.get(slug=need_slug)
    proposal = Proposal(need=need)
    form = ProposalForm(request.POST, instance=proposal)
    if form.is_valid():
        proposal = form.save()
        return redirect(view, need_slug, proposal.id)
    else:
        return render_to_response('proposal_edit.html', dict(form=form),
            context_instance=RequestContext(request))


def edit(request, need_slug, id):
    p = Proposal.objects.get(id=id)
    context = dict(form=ProposalForm(instance=p),
                   action=reverse('save_proposal', args=(need_slug,)))
    return render_to_response('proposal_edit.html', context,
            context_instance=RequestContext(request))
