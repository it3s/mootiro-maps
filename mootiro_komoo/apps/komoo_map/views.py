#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.http import HttpResponse

from komoo_map.models import get_editable_models_json

logger = logging.getLogger(__name__)


def feature_types(request):
    return HttpResponse(get_editable_models_json(),
        mimetype="application/x-javascript")

