import json
from django.contrib.gis.db import models as geomodels
from collection_from import CollectionFrom

from main.utils import create_geojson


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
