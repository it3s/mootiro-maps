#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default
import logging

from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.db.models.loading import get_model

from komoo_map.models import get_editable_models_json
from main.utils import create_geojson

logger = logging.getLogger(__name__)


def feature_types(request):
    logger.debug('accessing Komoo Map > feature_types')
    return HttpResponse(get_editable_models_json(),
        mimetype="application/x-javascript")

def geojson(request, app_label, model_name, obj_id):
    logger.debug('accessing Komoo Map > geojson')
    model = get_model(app_label, model_name)
    obj = get_object_or_404(model, id=obj_id) if model else None
    return HttpResponse(create_geojson([obj]),
        mimetype="application/x-javascript")

def tooltip(request, zoom, app_label, model_name, obj_id):
    logger.debug('accessing Komoo Map > tooltip')
    model = get_model(app_label, model_name)
    obj = get_object_or_404(model, id=obj_id) if model else None
    template = getattr(obj, 'tooltip_template', 'komoo_map/tooltip.html')
    return render_to_response(template,
            {'object': obj, 'zoom': zoom},
            context_instance=RequestContext(request))

def info_window(request, zoom, app_label, model_name, obj_id):
    logger.debug('accessing Komoo Map > info_window')
    model = get_model(app_label, model_name)
    obj = get_object_or_404(model, id=obj_id) if model else None
    template = getattr(obj, 'info_window_template', 'komoo_map/info_window.html')
    return render_to_response(template,
            {'object': obj, 'zoom': zoom},
            context_instance=RequestContext(request))
