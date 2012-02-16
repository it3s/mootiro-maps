#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils import simplejson
from django.core.urlresolvers import reverse

from annoying.decorators import render_to
from taggit.models import TaggedItem
from annoying.decorators import render_to, ajax_request

from community.models import Community
from need.models import Need, NeedTargetAudienceTag
from need.forms import NeedForm


@render_to('need/edit.html')
def edit(request, community_slug="", need_slug=""):
    # always receives both slugs or none of them
    if need_slug:
        community = get_object_or_404(Community, slug=community_slug)
        need = get_object_or_404(Need, slug=need_slug, community=community)
        action = reverse('edit_need', args=(community_slug, need_slug))
    else:
        need = None
        action = reverse('new_need')
    if request.POST:
        form = NeedForm(request.POST, instance=need)
        if form.is_valid():
            need = form.save()
            return redirect('view_need', community_slug=need.community.slug,
                        need_slug=need.slug)
        else:
            return {'form': form, 'action': action}
    else:
        return {'form': NeedForm(instance=need), 'action': action}

@render_to('need/view.html')
def view(request, community_slug, need_slug):
    community = get_object_or_404(Community, slug=community_slug)
    need = get_object_or_404(Need, slug=need_slug, community=community)
    return {'need': need}

def tag_search(request):
    term = request.GET['term']
    qset = TaggedItem.tags_for(NeedTargetAudienceTag).filter(name__istartswith=term)
    tags = [ t.name for t in qset ]
    return HttpResponse(simplejson.dumps(tags),
                mimetype="application/x-javascript")
