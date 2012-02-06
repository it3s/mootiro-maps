#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from .models import Proposal
from .forms import ProposalForm


def view(request, id):
    proposal = Proposal.objects.get(id=id)
    return render_to_response('proposal_view.html', dict(proposal=proposal))


def new(request):
    context = {
        'form': ProposalForm()
    }
    return render_to_response('proposal_edit.html', context,
            context_instance=RequestContext(request))


def save(request):
    form = ProposalForm(request.POST)
    p = form.save()
    # return redirect('komoo.proposal.views.view', p.id)
    # return redirect('view_proposal', p.id)
    return redirect(view, p.id)


def edit(request, id):
    p = Proposal.objects.get(id=id)
    return render_to_response('proposal_edit.html', {'proposal': p},
            context_instance=RequestContext(request))
