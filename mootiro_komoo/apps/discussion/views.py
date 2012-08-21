#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

import logging
from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None
from ajaxforms import ajax_form

from .models import Discussion
from community.models import Community
# from need.models import Need
# from komoo_resource.models import Resource
# from organization.models import OrganizationBranch, Organization
# from proposal.models import Proposal
from .forms import DiscussionForm

logger = logging.getLogger(__name__)


def _discussion_for (identifier):
    entity_model = {
        'c': Community,
    }
    entity, id_ = identifier[0], identifier[1:]
    obj = get_object_or_404(entity_model[entity], pk=id_)
    if not obj.discussion:
        print "\n\n\n = = = = = NOOOOOT = = = = = \n\n\n"
        d = Discussion()
        d.save()
        obj.discussion = d
        obj.save()
    else:
        print "\n\n\n = = = = = YESSSSS = = = = = \n\n\n"

    return obj


@render_to('discussion/view.html')
def view_discussion(request, identifier=''):
    obj = _discussion_for(identifier)
    return dict(obj=obj, menu_section=obj._meta.verbose_name)


@login_required
@ajax_form('discussion/edit.html', DiscussionForm)
def edit_discussion(request, identifier='', *args, **kwargs):
    logger.debug('acessing discussion > edit_discussion : identifier={}'
        ''.format(identifier))

    obj = _discussion_for(identifier)

    def on_get(request, form_discussion):
        return DiscussionForm(instance=obj.discussion)

    def on_after_save(request, discussion):
        url = reverse('view_discussion', args=(discussion.content_object.perm_id,))
        return {'redirect': url}

    return {'on_get': on_get, 'on_after_save': on_after_save,
            'obj': obj, 'menu_section': obj._meta.verbose_name}
