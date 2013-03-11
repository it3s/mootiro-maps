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

    if ish.inserted:
        url = reverse('importsheet_insert', args=(ish.id,))
        return redirect(url)

    wks = request.GET['worksheet_name'] if 'worksheet_name' in request.GET \
            else ish.spreadsheet.sheet1.title

    worksheet_interpreter = ish.simulate(wks)

    if worksheet_interpreter.rows:
        any_error = reduce(lambda a, b: a or b,
                        [bool(r.errors) for r in worksheet_interpreter.rows])
        empty = False
    else:
        any_error = False  # empty importsheet
        empty = True

    return dict(importsheet=ish, interpreter=worksheet_interpreter,
                empty=empty, any_error=any_error, user=request.user)


@render_to('importsheet/insert.html')
def insert(request, id=''):
    ish = Importsheet.objects.get(id=id)

    if not ish.inserted:
        if request.user.is_admin:
            success = ish.insert_all()
        else:
            url = reverse('importsheet_show', args=(ish.id,))
            return redirect(url)
    else:
        success = True

    return dict(success=success, importsheet=ish)


def undo(request, id=''):
    ish = Importsheet.objects.get(id=id)

    if ish.inserted:
        if request.user.is_admin:
            ish.undo()
        else:
            return redirect(reverse('importsheet_insert', args=(ish.id,)))
    
    return redirect(reverse('importsheet_show', args=(ish.id,)))
