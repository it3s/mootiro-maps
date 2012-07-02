import json
from django.contrib.gis.db import models as geomodels
from django.core.urlresolvers import reverse
from collection_from import CollectionFrom

from main.utils import create_geojson


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
    def geojson(self):
        geojson = create_geojson([self], convert=False)
        if geojson and geojson.get('features'):
            geojson['features'][0]['properties']['userCanEdit'] = True
        return json.dumps(geojson)

    class Meta:
        abstract = True

    class Map:
        editable = False


def get_models():
    return [model for model in GeoRefModel.__subclasses__()]

def get_editable_models():
    return [model for model in GeoRefModel.__subclasses__() \
                if getattr(model.Map, 'editable', False)]

def get_models_json(all=True):
    return json.dumps([{'type': model.__name__,
                    'categories': getattr(model.Map, 'categories', []),
                    'title': getattr(model.Map, 'title', '{}'.format(model.__name__)),
                    'tooltip': getattr(model.Map, 'tooltip', 'Add {}'.format(model.__name__)),
                    'color': getattr(model.Map, 'background_color', '#000'),
                    'border': getattr(model.Map, 'border_color', '#000'),
                    'icon': getattr(model.Map, 'icon_url', ''),
                    'overlayTypes': getattr(model.Map, 'geometries', []),
                    'formUrl': reverse(getattr(model.Map, 'form_view_name', 'root'), 
                        args=getattr(model.Map, 'form_view_args', []),
                        kwargs=getattr(model.Map, 'form_view_kwargs', {})),
                    'zIndex': 1,
                    'disabled': False,
                    } for model in (get_models() if all else get_editable_models())])

def get_editable_models_json():
    return get_models_json(False)
