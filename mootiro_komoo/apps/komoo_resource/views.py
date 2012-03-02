# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from annoying.decorators import render_to
from komoo_resource.models import Resource
from komoo_resource.forms import FormResource


@render_to('resource/list.html')
def index(request):
    resources = Resource.objects.all()
    return dict(resources=resources)


@render_to('resource/edit.html')
def edit(request):
    form_resource = FormResource()
    return dict(form_resource=form_resource)
