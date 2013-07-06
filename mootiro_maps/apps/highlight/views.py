#! coding: utf-8 -*-
from __future__ import unicode_literals
from annoying.decorators import render_to
from .models import HighlightSection

import logging
logger = logging.getLogger(__name__)


@render_to('highlight/project_highlights.html')
def project_highlights(request):
    hs = HighlightSection.objects.filter(page_name='/project', is_active=True)\
            .order_by('page_order')
    return dict(sections=hs)


@render_to('highlight/object_highlights.html')
def object_highlights(request):
    hs = HighlightSection.objects.filter(page_name='/object', is_active=True)\
            .order_by('page_order')
    return dict(sections=hs)
