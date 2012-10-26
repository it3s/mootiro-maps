# -*- coding: utf-8 -*-
'''
References:
    https://developers.google.com/accounts/docs/OAuth2WebServer#offline
    https://developers.google.com/api-client-library/python/reference/pydoc
    https://developers.google.com/apis-explorer/
'''
from __future__ import unicode_literals

from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from annoying.decorators import render_to

from authentication.utils import login_required
from models import Importsheet
from forms import FormImportsheet


@login_required
@render_to('importsheet/new.html')
def new(request):
    if request.method == 'POST':
        form = FormImportsheet(request.POST)
        if form.is_valid():
            ish = Importsheet(**form.cleaned_data)
            ish.creator = request.user
            ish.save()
            url = reverse('importsheet_show', args=(ish.id,))
            return redirect(url)
    else:
        form = FormImportsheet()
    return {'form': form}


@login_required
@render_to('importsheet/show.html')
def show(request, id=''):
    ish = Importsheet.objects.get(id=id)
    try:
        # TODO: name cannot be hardcoded
        parse_dicts = ish.simulate('Organizações')
    except KeyError as e:
        return dict(importsheet=ish, missing_column=e.message)

    if parse_dicts:
        any_error = reduce(lambda a, b: a or b,
                        [bool(od['errors']) for od in parse_dicts])
    else:
        any_error = True  # empty importsheet

    return dict(importsheet=ish, parse_dicts=parse_dicts, any_error=any_error)


@render_to('importsheet/insert.html')
def insert(request, id=''):
    ish = Importsheet.objects.get(id=id)
    success, data = ish.insert('Organizações')
    return dict(success=success, importsheet=ish, data=data)
