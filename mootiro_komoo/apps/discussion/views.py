#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.shortcuts import get_object_or_404

import logging
from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None

from .models import Discussion
from community.models import Community
# from need.models import Need
# from komoo_resource.models import Resource
# from organization.models import OrganizationBranch, Organization
# from proposal.models import Proposal

logger = logging.getLogger(__name__)


@render_to('discussion/discussion.html')
def discussion(request, identifier=''):
    entity_model = {
        'c': Community,
    }

    entity, id_ = identifier[0], identifier[1:]
    obj = get_object_or_404(entity_model[entity], pk=id_)

    if not obj.discussion and request.user.is_authenticated():
        obj.discussion = Discussion(creator=request.user, text="LALALA")
        obj.save()

    menu_section = dir(obj._meta.verbose_name)

    return dict(discussion=obj.discussion, obj=obj, menu_section=menu_section)
