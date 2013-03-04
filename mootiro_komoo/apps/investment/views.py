# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils import simplejson

from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from lib.taggit.models import TaggedItem
from ajaxforms import ajax_form

from authentication.utils import login_required

from proposal.models import Proposal
from investment.models import Investment
from investment.forms import InvestmentForm
from komoo_resource.models import Resource
from organization.models import Organization

from main.utils import paginated_query, filtered_query, sorted_query


logger = logging.getLogger(__name__)


def prepare_investment_objects(grantee_type='', grantee_id=None,
        investment_id=None):

    if grantee_type == 'proposal':
        grantee = get_object_or_None(Proposal, pk=grantee_id)
    elif grantee_type == 'organization':
        grantee = get_object_or_None(Organization, pk=grantee_id)
    elif grantee_type == 'resource':
        grantee = get_object_or_None(Resource, pk=grantee_id)
    else:
        grantee = None

    if investment_id:
        investment = get_object_or_404(Investment, pk=investment_id)
    else:
        investment = Investment(grantee=grantee)
    return investment


@login_required
@ajax_form('investment/edit.html', form_class=InvestmentForm)
def edit(request, id=None):
    grantee_type = request.GET.get('type', None)
    grantee_id = request.GET.get('obj', None)

    investment = prepare_investment_objects(investment_id=id,
            grantee_type=grantee_type, grantee_id=grantee_id)

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
def view(request, id=None):
    investment = get_object_or_404(Investment, pk=id)
    return dict(investment=investment)


@render_to('investment/list.html')
def list(request):
    sort_fields = ['creation_date', 'title']

    query_set = Investment.objects
    query_set = filtered_query(query_set, request)
    investments = sorted_query(query_set, sort_fields, request,
            default_order='title')

    investments_count = investments.count()
    investments = paginated_query(investments, request=request)
    return dict(investments=investments, investments_count=investments_count)


def tag_search(request):
    term = request.GET['term']
    qset = TaggedItem.tags_for(Investment).filter(name__istartswith=term)
    tags = [t.name for t in qset]
    return HttpResponse(simplejson.dumps(tags),
            mimetype="application/x-javascript")

