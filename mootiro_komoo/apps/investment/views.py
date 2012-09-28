# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils import simplejson

from annoying.decorators import render_to
from lib.taggit.models import TaggedItem
from ajaxforms import ajax_form

from proposal.views import prepare_proposal_objects
from organization.views import prepare_organization_objects
from komoo_resource.views import prepare_resource_objects
from investment.models import Investment
from investment.forms import InvestmentForm
from main.utils import paginated_query, filtered_query, sorted_query


logger = logging.getLogger(__name__)


def prepare_investment_objects(community_slug="", need_slug="",
        proposal_number="", organization_slug="", resource_id="",
        investment_slug=""):

    # determine the grantee to find the
    if proposal_number:
        # grantee is a proposal
        grantee, need = prepare_proposal_objects(need_slug, proposal_number)
    elif organization_slug:
        # grantee is an organization
        grantee = prepare_organization_objects(organization_slug)
    elif resource_id:
        # grantee is a resource
        grantee = prepare_resource_objects(resource_id)
    else:
        grantee = None

    if investment_slug:
        # TODO: make this query on a centralized place. Is it good enough here?
        investment = get_object_or_404(Investment, slug=investment_slug,
            grantee_content_type=ContentType.objects.get_for_model(grantee),
            grantee_object_id=grantee.id)
    else:
        investment = Investment(grantee=grantee)

    return investment


@login_required
@ajax_form('investment/edit.html', form_class=InvestmentForm)
def edit(request, need_slug="", proposal_number="",
        organization_slug="", resource_id="", investment_slug=""):

    kw = locals()
    kw.pop('request')
    investment = prepare_investment_objects(**kw)

    def on_get(request, form):  # necessary?
        data = {}
        if investment.investor:
            data = investment.investor.to_dict()
        return InvestmentForm(instance=investment, initial=data)

    def on_before_validation(request, form):
        return InvestmentForm(request.POST, instance=investment)

    def on_after_save(request, obj):
        return {'redirect': obj.view_url}

    return {'on_get': on_get, 'on_before_validation': on_before_validation,
            'on_after_save': on_after_save}


@render_to('investment/view.html')
def view(request, need_slug="", proposal_number="",
        organization_slug="", resource_id="", investment_slug=""):

    kw = locals()
    kw.pop('request')
    investment = prepare_investment_objects(**kw)

    return dict(investment=investment)


@render_to('investment/list.html')
def list(request):
    sort_fields = ['creation_date', 'votes', 'title']

    query_set = Investment.objects
    query_set = filtered_query(query_set, request)
    investments = sorted_query(query_set, sort_fields, request,
            default_order='title')

    investments = paginated_query(investments, request=request)
    return dict(investments=investments)


def tag_search(request):
    term = request.GET['term']
    qset = TaggedItem.tags_for(Investment).filter(name__istartswith=term)
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
            mimetype="application/x-javascript")

