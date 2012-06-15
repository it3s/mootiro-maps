#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import logging
import itertools

from annoying.decorators import render_to
from reversion.models import Version, VERSION_DELETE

from .models import Update


logger = logging.getLogger(__name__)


@render_to("update/frontpage.html")
def frontpage(request):
    logger.debug('acessing update > frontpage')

    # FIXME: this is too slow!!!
    updates_number = 100
    updates = Update.objects.order_by("-date")[0:100]

    return {'updates': updates}
