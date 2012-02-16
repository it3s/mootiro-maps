#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse

from annoying.decorators import render_to

from community.models import Community
from community.forms import CommunityForm, CommunityMapForm


@render_to('community/community_edit.html')
def edit(request, community_slug=""):
    if community_slug:
        community = get_object_or_404(Community, slug=community_slug)
        action = reverse('edit_community', args=(community_slug,))
    else:
        community = None
        action = reverse('new_community')
    if request.POST:
        form = CommunityForm(request.POST, instance=community)
        if form.is_valid():
            community = form.save()
            return redirect(view, community.slug)
        else:
            return {'form': form, 'action': action}
    else:
        return {'form': CommunityForm(instance=community), 'action': action}


@render_to('community/community_view.html')
def view(request, community_slug):
    community = get_object_or_404(Community, slug=community_slug)
    return {'community': community}

@render_to('community/community_map.html')
def map(request):
    #TODO: Use FormWizard.
    form = CommunityMapForm(request.POST)

    return dict(form=form)


def search_by_name(request):
    term = request.GET['term']
    rx = "^{0}|\s{0}".format(term)  # matches only beginning of words
    communities = Community.objects.filter(name__iregex=rx)
    d = [{'value': c.id, 'label': c.name} for c in communities]
    return HttpResponse(simplejson.dumps(d),
        mimetype="application/x-javascript")
