# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import simplejson

from annoying.decorators import render_to
from lib.taggit.models import TaggedItem

from proposal.views import prepare_proposal_objects
from organization.views import prepare_organization_objects
from komoo_resource.views import prepare_resource_objects
from investment.models import Investment
from investment.forms import InvestmentForm
from main.utils import create_geojson

logger = logging.getLogger(__name__)


def prepare_investment_objects(community_slug="", need_slug="",
        proposal_number="", organization_slug="", resource_id="",
        investment_slug=""):

    # determine the grantee to find the
    if proposal_number:
        # grantee is a proposal
        grantee, need, community = prepare_proposal_objects(community_slug,
            need_slug, proposal_number)
    elif organization_slug:
        # grantee is an organization
        grantee, community = prepare_organization_objects(community_slug,
            organization_slug)
    elif resource_id:
        # grantee is a resource
        grantee, community = prepare_resource_objects(community_slug,
            resource_id)
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
        organization_slug="", resource_id="", investment_slug=""):
    logger.debug('acessing investment > edit_<grantee>_investment')

    kw = locals()
    kw.pop('request')
    investment, community = prepare_investment_objects(**kw)

    if request.POST:
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            investment = form.save(commit=False)
            investor = form.cleaned_data['investor']
            investor.save()
            investment.investor = investor
            if not investment.id:  # was never saved
                investment.creator = request.user
            investment.save()

            # why need to explicit save tags here?
            investment = form.save(commit=False)
            tags = form.cleaned_data['tags']
            investment.tags.set(*tags)
            investment.save()

            # FIXME: this only works for Proposals
            return redirect(investment.view_url)
    else:
        data = {}
        if investment.investor:
            data = investment.investor.to_dict()
        form = InvestmentForm(instance=investment, initial=data)

    return dict(form=form, community=community)


@render_to('investment/view.html')
def view(request, community_slug="", need_slug="", proposal_number="",
        organization_slug="", resource_id="", investment_slug=""):
    logger.debug('acessing investment > view_<grantee>_investment')

    kw = locals()
    kw.pop('request')
    investment, community = prepare_investment_objects(**kw)

    return dict(investment=investment, community=community)


def tag_search(request):
    logger.debug('acessing investment > tag_search')
    term = request.GET['term']
    qset = TaggedItem.tags_for(Investment).filter(name__istartswith=term)
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
                mimetype="application/x-javascript")
