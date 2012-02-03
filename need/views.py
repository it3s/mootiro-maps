#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.shortcuts import render_to_response
from django.template import RequestContext
from need.forms import NeedForm


def new(request):
    context = {
        'form': NeedForm()
    }
    return render_to_response('need_edit.html', context,
            context_instance=RequestContext(request))

def save(request):
    need = NeedForm(request.POST)
    need.save()
    return render_to_response('need_edit.html')
