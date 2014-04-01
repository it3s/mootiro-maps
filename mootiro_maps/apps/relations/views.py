# -*- encoding: utf-8 -*-
from django.http import HttpResponse
from main.utils import to_json


def edit_relations(request):
    print 'EDIT RELATIONS', request
    return HttpResponse()

def search_relations(request):
    print "SEARCH RELATIONS", request
    results = [{'label': "blabla", 'value': '1'}, {'label': "blebleble", 'value': '2'}]
    return HttpResponse(to_json(results),
                        mimetype="application/x-javascript")
