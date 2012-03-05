#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # unicode by default

import json
import re
import collections

from django.template.defaultfilters import slugify as simple_slugify

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset


def slugify(term, slug_exists=lambda s: False):
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


def create_geojson(objects, type_='FeatureCollection', convert=True):
    if type_ == 'FeatureCollection':
        geojson = {
            'type': 'FeatureCollection',
            'features': []
        }

        for obj in objects:
            type_ = obj.__class__.__name__.lower()
            geometry = json.loads(obj.geometry.geojson) if \
                    type_ == 'community' else \
                    json.loads(obj.geometry.geojson)['geometries'][0]
            name = getattr(obj, 'name', getattr(obj, 'title', ''))
            feature = {
                'type': 'Feature',
                'geometry': geometry,
                'properties': {
                    'type': type_,
                    'name': name,
                }
            }
            if hasattr(obj, 'community'):
                feature['properties']['community_slug'] = getattr(obj.community, 'slug', '')
            if hasattr(obj, 'slug'):
                feature['properties']['{}_slug'.format(type_)] = obj.slug

            geojson['features'].append(feature)

    if convert:
        return json.dumps(geojson)

    return geojson


class MooHelper(FormHelper):
    def __init__(self, *a, **kw):
        retorno = super(MooHelper, self).__init__(*a, **kw)
        self.add_input(Submit('submit', 'Submit'))
        self.add_input(Reset('reset', 'Reset'))
        return retorno
