#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import re

from django.template.defaultfilters import slugify as simple_slugify


def slugify(term, slug_exists):
    """Receives a term and a validator for the created slug in a namespace.
    Returns a slug that is unique according to the validator.
    """
    original = simple_slugify(term)
    slug = original
    n = 2
    # If needed, append unique number prefix to slug
    while slug_exists(slug):
        slug = re.sub(r'\d+$', '', slug)  # removes trailing '-number'
        slug = original + '-' + str(n)
        n += 1
    return slug
