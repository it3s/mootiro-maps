#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse

from annoying.decorators import render_to, ajax_request
from taggit.models import TaggedItem

from community.models import Community
from need.models import Need
from need.forms import NeedForm

logger = logging.getLogger(__name__)


@render_to('need/edit.html')
def edit(request, community_slug="", need_slug=""):
    logger.debug('acessing need > edit')
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
    logger.debug('acessing need > view')
    community = get_object_or_404(Community, slug=community_slug)
    need = get_object_or_404(Need, slug=need_slug, community=community)
    return {'need': need}


@ajax_request
def tag_search(request):
    logger('acessing nedd > tag_search')
    term = request.GET['term']
    qset = TaggedItem.tags_for(Need).filter(name__istartswith=term)
    tags = [t.name for t in qset]
    return tags
