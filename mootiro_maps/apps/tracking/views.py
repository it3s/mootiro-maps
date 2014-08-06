#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import logging
from django.http import HttpResponse, HttpResponseRedirect

from authentication.utils import login_required, access_key_required
from .models import Tracking
from main.utils import to_json

logger = logging.getLogger(__name__)

def count_unique_visits(request):
    url = request.GET.get('url', None)
    count = Tracking.count_unique_visits_for(url)
    return HttpResponse(count)

def count_visits(request):
    url = request.GET.get('url', None)
    count = Tracking.count_visits_for(url)
    return HttpResponse(count)

@access_key_required
def list_visits(request):
    url = request.GET.get('url', None)
    list_ = to_json({'visits': [{'visitorId': t.visitor_id,
                                   'visitorName': getattr(t.visitor, 'name', 'anonymous'),
                                   'visitorEmail': getattr(t.visitor, 'email', '-'),
                                   'visitorOrganization': getattr(t.visitor, 'organization', '-'),
                                   'visitorCountry': getattr(t.visitor, 'country', '-'),
                                   'visitedDate': t.visited_date}
                                    for t in Tracking.get_visits_for(url) if t],
                     'count': Tracking.count_visits_for(url),
                     'unique': Tracking.count_unique_visits_for(url)})
    return HttpResponse(list_)

def redirect(request):
    url = request.GET.get('url', None)
    pass_ = request.GET.get('pass', False)
    if request.user.is_authenticated() or pass_:
        tracking = Tracking(url=url, ip_address=get_client_ip(request))
        if request.user.is_authenticated():
          tracking.visitor = request.user
        tracking.save()
    else:
        return authenticate(request)

    return  HttpResponseRedirect(url)

@login_required
def authenticate(request):
    return HttpResponse("authenticate")

PRIVATE_IPS_PREFIX = ('10.', '172.', '192.', )

def get_client_ip(request):
    """get the client ip from the request
    """
    remote_address = request.META.get('REMOTE_ADDR')
    # set the default value of the ip to be the REMOTE_ADDR if available
    # else None
    ip = remote_address
    # try to get the first non-proxy ip (not a private ip) from the
    # HTTP_X_FORWARDED_FOR
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        proxies = x_forwarded_for.split(',')
        # remove the private ips from the beginning
        while (len(proxies) > 0 and
                proxies[0].startswith(PRIVATE_IPS_PREFIX)):
            proxies.pop(0)
        # take the first ip which is not a private one (of a proxy)
        if len(proxies) > 0:
            ip = proxies[0]

    return ip
