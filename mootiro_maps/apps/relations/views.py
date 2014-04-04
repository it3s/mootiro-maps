# -*- encoding: utf-8 -*-
from django.http import HttpResponse
from main.utils import to_json
from search.utils import search_by_term


def edit_relations(request):
    print '\n\nEDIT RELATIONS', request.POST
    return HttpResponse()

def search_relations(request):
    term = request.GET.get('term', '')
    raw_results = search_by_term(term)
    results = [{'label': item['name'], 'value': item['id']} for item in raw_results]
    return HttpResponse(to_json(results),
                        mimetype="application/x-javascript")
