# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse

from annoying.decorators import render_to
from lib.taggit.models import TaggedItem
from ajaxforms import ajax_form

from proposal.views import prepare_proposal_objects
from organization.views import prepare_organization_objects
from komoo_resource.views import prepare_resource_objects
from investment.models import Investment
from investment.forms import InvestmentForm
from community.models import Community
from main.utils import paginated_query

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


@login_required
@ajax_form('investment/edit.html', form_class=InvestmentForm)
def edit(request, community_slug="", need_slug="", proposal_number="",
        organization_slug="", resource_id="", investment_slug=""):
    logger.debug('acessing investment > new')

    kw = locals()
    kw.pop('request')
    investment, community = prepare_investment_objects(**kw)

    def on_get(request, form):  # necessary?
        data = {}
        if investment.investor:
            data = investment.investor.to_dict()
        return InvestmentForm(instance=investment, initial=data)

    def on_before_validation(request, form):
        return InvestmentForm(request.POST, instance=investment)

    def on_after_save(request, obj):
        return {'redirect': reverse('investment_list')}

    return {'on_get': on_get, 'on_before_validation': on_before_validation,
            'on_after_save': on_after_save, 'community': community}


@render_to('investment/view.html')
def view(request, community_slug="", need_slug="", proposal_number="",
        organization_slug="", resource_id="", investment_slug=""):
    logger.debug('acessing investment > view_<grantee>_investment')

    kw = locals()
    kw.pop('request')
    investment, community = prepare_investment_objects(**kw)

    return dict(investment=investment, community=community)


@render_to('investment/list.html')
def list(request, community_slug=''):
    logger.debug('acessing investment > list')
    if community_slug:
        community = get_object_or_404(Community, slug=community_slug)
        investments = Investment.objects.all().order_by('title')
    else:
        community = None
        investments = Investment.objects.all().order_by('title')
    investments = paginated_query(investments, request=request)
    return dict(investments=investments, community=community)


def tag_search(request):
    logger.debug('acessing investment > tag_search')
    term = request.GET['term']
    qset = TaggedItem.tags_for(Investment).filter(name__istartswith=term)
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
                mimetype="application/x-javascript")
