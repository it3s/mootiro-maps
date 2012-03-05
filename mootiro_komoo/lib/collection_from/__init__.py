# Copyright (c) 2011 Philip Neustrom <philipn@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from django.contrib.gis.db import models
from django.contrib.gis.geos import *

class CollectionFrom(models.GeometryCollectionField):
    """
    Creates a GeometryCollection pseudo-field from the provided
    component fields. When accessed, the CollectionFrom field will
    return a GeometryCollection from the provided component fields.
    When set to a value (upon model save) the geometries contained in
    the CollectionFrom field are broken out and placed into their
    relevant component fields.

    Example::

        class MyModel(models.Model):
            points = models.MultiPointField()
            lines = models.MultiLineStringField()
            polys = models.MultiPolygonField()
            geom = CollectionFrom(points='points', lines='lines',
                polys='polys')

    Then when you access the 'geom' attribute on instances of MyModel
    you'll get a GeometryCollection with your points, lines and polys.
    When you set the 'geom' attribute to a GeometryCollection and save
    an instance of MyModel the GeometryCollection is broken into points,
    lines and polygons and placed into the provided fields.

    This field is useful when you want to deal with GeometryCollections
    but still must maintain separate geometry fields on the model. For
    instance, GeoDjango does not currently allow you to filter (with
    geometry operations) based on GeometryCollections due to issues
    with the underlying libraries. Someday this may be fixed. But
    until then, we've got this Field.

    NOTES: This field will add a column to the db, but it won't ever
           store anything there except null. There's probably a way
           around this. TODO.
    """
    def __init__(self, *args, **kwargs):
        self.points_name = kwargs.pop('points') if 'points' in kwargs else None
        self.lines_name = kwargs.pop('lines') if 'lines' in kwargs else None
        self.polys_name = kwargs.pop('polys') if 'polys' in kwargs else None

        super(CollectionFrom, self).__init__(*args, **kwargs)
        self.null = True

    def contribute_to_class(self, cls, name):
        models.signals.class_prepared.connect(self.finalize, sender=cls)
        setattr(cls, name, CollectionDescriptor(self))
        super(models.GeometryField, self).contribute_to_class(cls, name)

    def finalize(self, sender, **kws):
        self._connected_to = sender
        models.signals.pre_save.connect(self.pre_model_save, sender=sender,
            weak=False)

    def pre_model_save(self, instance, raw, **kws):
        if not 'sender' in kws:
            return
        geom_collection = instance.__dict__.get(
            '_explicit_set_%s' % self.attname, None)
        if geom_collection is None:
            # They didn't set an explicit GeometryCollection.
            return
        points, lines, polys = [], [], []
        points_geom, lines_geom, polys_geom = None, None, None
        for geom in geom_collection:
            if type(geom) is Point:
                points.append(geom)
            if type(geom) is MultiPoint:
                points += [g for g in geom]
            if type(geom) is LineString or type(geom) is LinearRing:
                lines.append(geom)
            if type(geom) is MultiLineString:
                lines += [g for g in geom]
            if type(geom) is Polygon:
                polys.append(geom)
            if type(geom) is MultiPolygon:
                polys += [g for g in geom]

        if points:
            points_geom = MultiPoint(points, srid=points[0].srid)
        if lines:
            lines_geom = MultiLineString(lines, srid=lines[0].srid)
        if polys:
            polys_geom = MultiPolygon(polys, srid=polys[0].srid)

        setattr(instance, self.points_name, points_geom)
        setattr(instance, self.lines_name, lines_geom)
        setattr(instance, self.polys_name, polys_geom)

        # Set ourself to None to avoid saving any data in our column.
        setattr(instance, self.name, None)
        instance.__dict__[self.name] = None


class CollectionDescriptor(object):
    def __init__(self, field):
        self._field = field

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self._field.name, owner.__name__))

        set_field_value = instance.__dict__.get(
            '_explicit_set_%s' % self._field.attname, None)
        if set_field_value:
            # Return the value they set for the field rather than our
            # constructed GeometryCollection.
            return set_field_value

        enum_points, enum_lines, enum_polys = [], [], []
        points = getattr(instance, self._field.points_name)
        if points:
            enum_points = [p for p in points]
        lines = getattr(instance, self._field.lines_name)
        if lines:
            enum_lines = [l for l in lines]
        polys = getattr(instance, self._field.polys_name)
        if polys:
            enum_polys = [p for p in polys]

        geoms = enum_points + enum_lines + enum_polys
        return GeometryCollection(geoms, srid=self._field.srid)

    def __set__(self, obj, value):
        # The OGC Geometry type of the field.
        gtype = self._field.geom_type

        # The geometry type must match that of the field -- unless the
        # general GeometryField is used.
        if (isinstance(value, GeometryCollection) and
            (str(value.geom_type).upper() == gtype or gtype == 'GEOMETRY')):
            # Assigning the SRID to the geometry.
            if value.srid is None:
                value.srid = self._field.srid
        elif value is None:
            pass
        elif isinstance(value, (basestring, buffer)):
            # Set with WKT, HEX, or WKB
            value = GEOSGeometry(value, srid=self._field.srid)
        else:
            raise TypeError(
                'cannot set %s CollectionFrom with value of type: %s' %
                (obj.__class__.__name__, type(value)))

        obj.__dict__['_explicit_set_%s' % self._field.attname] = value
        return value
