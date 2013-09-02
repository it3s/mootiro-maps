#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
from annoying.decorators import render_to


@render_to('hotsite/root.html')
def root(request):
    return dict()

@render_to('hotsite/about.html')
def about(request):
    return dict()

