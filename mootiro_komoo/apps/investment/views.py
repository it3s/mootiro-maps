# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from community.models import Community
from proposal.views import prepare_proposal_objects
from investment.forms import InvestmentForm

logger = logging.getLogger(__name__)


def _determine_grantee(community_slug="", need_slug="", proposal_number="",
        organization_slug="", resource_slug="", investment_slug=""):
    if proposal_number:
        # grantee is a need proposal
        grantee, need, community = prepare_proposal_objects(community_slug,
            need_slug, proposal_number)
    elif organization_slug:
        # grantee is an organization
        pass
    elif resource_slug:
        # grantee is a resource
        pass
    else:
        grantee = community = None

    return dict(grantee=grantee, community=community)


@render_to('investment/edit.html')
@login_required
def edit(request, community_slug="", need_slug="", proposal_number="",
        organization_slug="", resource_slug="", investment_slug=""):
    logger.debug('acessing investment > edit_proposal_investment')

    community = get_object_or_None(Community, slug=community_slug)

    # d = _determine_grantee(community_slug, need_slug, proposal_number,
    #     organization_slug, resource_slug, investment_slug)

    # first of all, determine grantee based on url
    return dict(form=InvestmentForm(), community=community)
