#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import logging

from annoying.decorators import render_to

from community.forms import CommunityMapForm

logger = logging.getLogger(__name__)


@render_to('main/root.html')
def root(request):
    logger.debug('acessing Root')
    form = CommunityMapForm(request.POST)

    return dict(form=form)


