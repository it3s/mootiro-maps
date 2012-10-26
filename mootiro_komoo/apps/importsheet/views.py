# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from annoying.decorators import render_to


@render_to('importsheet/poc.html')
def poc(request):
    return dict()
