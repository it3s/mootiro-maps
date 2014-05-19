# -*- encoding: utf-8 -*-
import simplejson as json
import re
from urlparse import urlparse
from django.shortcuts import HttpResponse, redirect
from django.core.urlresolvers import reverse
from main.utils import to_json
from search.utils import search_by_term
from relations.models import Relation

def _back_url(request):
    back_url = urlparse(request.META['HTTP_REFERER']).path.replace('/edit', '')
    if "community" in back_url:
        back_url += "/about"
    return back_url

def edit_relations(request):
    print "\n\n"
    print json.loads(request.POST['relations_json'])
    print "\n\n"
    Relation.edit(request.POST['object_oid'], json.loads(request.POST['relations_json']))
    return redirect(_back_url(request))

def search_relations(request):
    term = request.GET.get('term', '')
    raw_results = search_by_term(term)
    results = [{'label': item['name'], 'value': item['id']} for item in raw_results]
    return HttpResponse(to_json(results),
                        mimetype="application/x-javascript")
