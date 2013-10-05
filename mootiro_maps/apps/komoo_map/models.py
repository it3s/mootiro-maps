# -*- coding: utf-8 -*-
import json
import os

from django.conf import settings
from django.contrib.gis.db import models as geomodels
from django.core.urlresolvers import reverse
from collection_from import CollectionFrom

from main.utils import create_geojson, to_json
from fileupload.models import UploadedFile


POLYGON = 'Polygon'
LINESTRING = 'LineString'
MULTILINESTRING = 'MultiLineString'
POINT = 'Point'
MULTIPOINT = 'MultiPoint'


class GeoRefModel(geomodels.Model):
    """Abstract class to use on any model we want geo spatial information"""
    # Geolocalization attributes
    objects = geomodels.GeoManager()

    points = geomodels.MultiPointField(null=True, blank=True, editable=False)
    lines = geomodels.MultiLineStringField(null=True, blank=True, editable=False)
    polys = geomodels.MultiPolygonField(null=True, blank=True, editable=False)
    geometry = CollectionFrom(points='points', lines='lines', polys='polys')


    @property
    def related_items(self):
        return []

    def is_empty(self):
        return self.geometry.empty

    @property
    def area(self):
        geo = self.geometry.transform(32118, clone=True)
        return self.geometry.area
        return geo.area

    @property
    def geojson(self):
        geojson = create_geojson([self], convert=False)
        if geojson and geojson.get('features'):
            geojson['features'][0]['properties']['userCanEdit'] = True
            geojson['features'][0]['properties']['alwaysVisible'] = True
        return to_json(geojson)

    class Meta:
        abstract = True

    class Map:
        editable = False

        title = ''
        tooltip = ''

        background_color = '#000'
        background_opacity = 0.6
        border_color = '#000'
        border_opacity = 0.6
        border_size = 1.5
        border_size_hover = 2.5

        geometries = []
        categories = []

        form_view_name = ''
        form_view_args = []
        form_view_kwargs = {}

        min_zoom_geometry = 16
        max_zoom_geometry = 100
        min_zoom_point = 14
        max_zoom_point = 15
        min_zoom_icon = 18
        max_zoom_icon = 100

        zindex = 10

    @classmethod
    def get_map_attr(cls, attr_name):
        value = getattr(cls.Map, attr_name,
                        getattr(GeoRefModel.Map, attr_name))
        return value

    # FIXME: files_set and logo_url should live in other class. They must be
    # moved when we get unified model.
    def files_set(self):
        """ pseudo-reverse query for retrieving Resource Files"""
        return UploadedFile.get_files_for(self)

    # FIXME: files_set and logo_url should live in other class. They must be
    # moved when we get unified model.
    @property
    def logo_url(self):
        url = getattr(self, 'default_logo_url', 'img/logo-fb.png')
        url = '{}{}'.format(settings.STATIC_URL, url)
        files = self.files_set()
        for fl in files:
            if os.path.exists(fl.file.url[1:]):
                url = fl.file.url
                break
        return url


def get_models():
    return [model for model in GeoRefModel.__subclasses__()]


def get_editable_models():
    return [model for model in get_models()
                if getattr(model.Map, 'editable', False)]


def get_models_json(all=True):
    return to_json([{'type': model.__name__,
                    'appLabel': model._meta.app_label,
                    'modelName': model.__name__,
                    'disabled': not model.get_map_attr('editable'),
                    'title': model.get_map_attr('title') or '{}'.format(model.__name__),
                    'tooltip': model.get_map_attr('tooltip') or 'Add {}'.format(model.__name__),
                    'backgroundColor': model.get_map_attr('background_color'),
                    'backgroundOpacity': model.get_map_attr('background_opacity'),
                    'borderColor': model.get_map_attr('border_color'),
                    'borderOpacity': model.get_map_attr('border_opacity'),
                    'borderSize': model.get_map_attr('border_size'),
                    'borderSizeHover': model.get_map_attr('border_size_hover'),
                    'geometryTypes': model.get_map_attr('geometries'),
                    'categories': model.get_map_attr('categories'),
                    'formUrl': reverse(model.get_map_attr('form_view_name'),
                        args=model.get_map_attr('form_view_args'),
                        kwargs=model.get_map_attr('form_view_kwargs'))
                                if model.get_map_attr('editable') else '',
                    'minZoomGeometry': model.get_map_attr('min_zoom_geometry'),
                    'maxZoomGeometry': model.get_map_attr('max_zoom_geometry'),
                    'minZoomPoint': model.get_map_attr('min_zoom_point'),
                    'maxZoomPoint': model.get_map_attr('max_zoom_point'),
                    'minZoomIcon': model.get_map_attr('min_zoom_icon'),
                    'maxZoomIcon': model.get_map_attr('max_zoom_icon'),
                    'zIndex': model.get_map_attr('zindex'),
                    } for model in (get_models() if all else get_editable_models())])


def get_editable_models_json():
    return get_models_json(False)

