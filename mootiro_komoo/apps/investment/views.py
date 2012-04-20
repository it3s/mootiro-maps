# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect, get_object_or_404

from annoying.decorators import render_to

from proposal.views import prepare_proposal_objects
from investment.models import Investment
from investment.forms import InvestmentForm
from main.utils import create_geojson

logger = logging.getLogger(__name__)


def prepare_investment_objects(community_slug="", need_slug="",
        proposal_number="", organization_slug="", resource_slug="",
        investment_slug=""):

    # determine the grantee to find the
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

    if investment_slug:
        # TODO: make this query on a centralized place. Is it good enough here?
        investment = get_object_or_404(Investment, slug=investment_slug,
            grantee_content_type=ContentType.objects.get_for_model(grantee),
            grantee_object_id=grantee.id)
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
        form = InvestmentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            investment = Investment(**data)
            investment.save()

            if not investment.id:  # was never saved
                investment.creator = request.user
            investment.save()

            # FIXME: this only works for Proposals
            kw = investment.home_url_params()
            return redirect('view_investment', **kw)
    else:
        print "GEEEET = = =", investment.investor
        form = InvestmentForm()

    return dict(form=form, community=community)


@render_to('investment/view.html')
def view(request, community_slug="", need_slug="", proposal_number="",
        organization_slug="", resource_slug="", investment_slug=""):
    logger.debug('acessing investment > view_<grantee>_investment')

    kw = locals()
    kw.pop('request')
    investment, community = prepare_investment_objects(**kw)
    geojson = create_geojson([investment.grantee.need])

    return dict(investment=investment, community=community, geojson=geojson)
