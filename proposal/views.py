#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.shortcuts import render_to_response
from django.template import RequestContext
from .models import Proposal
from .forms import ProposalForm


def new(request):
    context = {
        'form': ProposalForm()
    }
    return render_to_response('edit_proposal.html', context,
            context_instance=RequestContext(request))

def save(request):
    ProposalForm(request.POST).save()
    return render_to_response('edit_proposal.html')

def edit(request, slug):
    p = Proposal.objects.get(slug=slug)
    return render_to_response('edit_proposal.html', {'proposal': p},
            context_instance=RequestContext(request))
