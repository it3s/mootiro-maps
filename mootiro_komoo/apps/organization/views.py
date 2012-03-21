# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (render_to_response, RequestContext,
    get_object_or_404)
from django import forms

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from organization.models import Organization
from organization.forms import FormOrganization
from community.models import Community
from main.utils import paginated_query

logger = logging.getLogger(__name__)


@render_to('organization/list.html')
def organization_list(request, community_slug=''):
    community = get_object_or_None(Community, slug=community_slug)
    organizations = paginated_query(Organization.objects.all(), request)

    return dict(community=community, organizations=organizations)


class Edit(View):
    """Class based view for editing a Organization"""

    @method_decorator(login_required)
    def get(self, request, community_slug=None, *args, **kwargs):
        logger.debug('acessing organization > Edit with GET')
        community = get_object_or_None(Community, slug=community_slug)

        _id = request.GET.get('id', None)
        if _id:
            organization = get_object_or_404(Organization, pk=_id)
            form_org = FormOrganization(instance=organization)
        else:
            form_org = FormOrganization()

        if community:
            form_org.fields['community'].widget = forms.HiddenInput()
            form_org.initial['community'] = community.id

        # tmplt = 'resource/edit.html' if _id else 'resource/new.html'
        tmplt = 'organization/edit.html'
        return render_to_response(tmplt,
            dict(form_org=form_org, community=community),
            context_instance=RequestContext(request))
