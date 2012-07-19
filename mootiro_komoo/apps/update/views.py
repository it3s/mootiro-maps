#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import logging
import itertools

from annoying.decorators import render_to
from reversion.models import Version, VERSION_DELETE

from main.utils import paginated_query, sorted_query, filtered_query
from .models import Update, News


logger = logging.getLogger(__name__)


@render_to("update/frontpage.html")
def frontpage(request):
    logger.debug('acessing update > frontpage')
    filters = request.GET.get('filters', [])
    if filters:
        filters = filters.split(',')

    if filters:
        query_set = Update.objects.filter(object_type__in=filters)
    else:
        query_set = Update.objects.all()
    sort_order = ['-date', 'comments_count']
    updates_list = sorted_query(query_set, sort_order, request, default_order='-date')
    updates_count = updates_list.count()
    updates = paginated_query(updates_list, request, size=30)

    news = News.objects.order_by("-date")

    return dict(updates=updates, news=news)
