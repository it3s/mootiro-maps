# -*- encoding: utf-8 -*-
from django.http import HttpResponse

def edit_relations(request):
    print 'EDIT RELATIONS', request
    return HttpResponse()
