#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.db.models.loading import get_model

from komoo_map.models import get_models_json
from main.utils import create_geojson


def feature_types(request):
    return HttpResponse(get_models_json(),
        mimetype="application/x-javascript")


def geojson(request, app_label, model_name, obj_id):
    model = get_model(app_label, model_name)
    obj = get_object_or_404(model, id=obj_id) if model else None
    geojson = getattr(obj, 'geojson', create_geojson([obj]))
    return HttpResponse(geojson,
        mimetype="application/x-javascript")


def related(request, app_label, model_name, obj_id):
    model = get_model(app_label, model_name)
    obj = get_object_or_404(model, id=obj_id) if model else None
    return HttpResponse(create_geojson(getattr(obj, 'related_items', [])),
        mimetype="application/x-javascript")


def tooltip(request, zoom, app_label, model_name, obj_id):
    model = get_model(app_label, model_name)
    obj = get_object_or_404(model, id=obj_id) if model else None
    template = getattr(obj, 'tooltip_template', 'komoo_map/tooltip.html')
    return render_to_response(template,
            {'object': obj, 'zoom': zoom},
            context_instance=RequestContext(request))


def info_window(request, zoom, app_label, model_name, obj_id):
    model = get_model(app_label, model_name)
    obj = get_object_or_404(model, id=obj_id) if model else None
    template = getattr(obj, 'info_window_template', 'komoo_map/info_window.html')
    return render_to_response(template,
            {'object': obj, 'zoom': zoom},
            context_instance=RequestContext(request))
