# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from community.models import Community
from proposal.views import prepare_proposal_objects
from investment.models import Investment
from investment.forms import InvestmentForm

logger = logging.getLogger(__name__)


def prepare_investment_objects(community_slug="", need_slug="",
        proposal_number="", organization_slug="", resource_slug="",
        investment_slug=""):

    # determine the grantee to find the
    if proposal_number:
        # grantee is a need proposal
        print "GRANTEE IS A PROPOSAL"
        grantee, need, community = prepare_proposal_objects(community_slug,
            need_slug, proposal_number)
        print grantee, need, community
    elif organization_slug:
        # grantee is an organization
        pass
    elif resource_slug:
        # grantee is a resource
        pass
    else:
        grantee = community = None

    if investment_slug:
        # FIXME: probably grantee must be filtered by its content_object
        #investment = get_object_or_404(Investment, slug=investment_slug,
        #                grantee_content_type=,
        #                grantee_object_id=grantee.id)
        pass
    else:
        investment = Investment(grantee=grantee)

    return investment, community


@render_to('investment/edit.html')
@login_required
def edit(request, community_slug="", need_slug="", proposal_number="",
        organization_slug="", resource_slug="", investment_slug=""):
    logger.debug('acessing investment > edit_<grantee>_investment')

    kw = locals()
    kw.pop('request')
    investment, community = prepare_investment_objects(**kw)

    if request.POST:
        print "POST"
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            print "GRANTEE = = = =", investment.grantee
            investment = form.save(commit=False)
            if not investment.id:  # was never saved
                investment.creator = request.user
            investment.save()

            # FIXME: this only works for Proposals
            kw = investment.home_url_params()
            print "KW = = = =", kw
            return redirect('view_investment', **kw)
        else:
            print "INVALID!!", form.errors
            return dict(form=form, community=community)
    else:
        return dict(form=InvestmentForm(instance=investment),
                        community=community)


@render_to('investment/view.html')
def view(request, community_slug="", need_slug="", proposal_number="",
        organization_slug="", resource_slug="", investment_slug=""):
    logger.debug('acessing investment > view_<grantee>_investment')

    kw = locals()
    kw.pop('request')
    print "KW = = = = = =", kw
    investment, community = prepare_investment_objects(**kw)

    return dict(investment=investment, community=community)
