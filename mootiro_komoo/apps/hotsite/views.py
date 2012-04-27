#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import logging

from annoying.decorators import render_to

logger = logging.getLogger(__name__)


@render_to('hotsite/root.html')
def root(request):
    logger.debug('acessing Hotsite')
    return dict()

@render_to('hotsite/about.html')
def about(request):
    logger.debug('acessing Hotsite > About')
    return dict()

