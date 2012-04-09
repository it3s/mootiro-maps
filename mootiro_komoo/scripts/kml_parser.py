#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import codecs
from xml.dom import minidom
from django.template.defaultfilters import slugify

obj_list = []


def generate_fixture():
    with codecs.open('fixture.json', 'w', 'utf-8') as f:
        f.write('[')
        for i, obj in enumerate(obj_list):
            if i > 0:
                f.write("  ,")
            f.write(u"""
  {
    "model": "organization.organization",
    "pk" : "%(num)s",
    "fields": {
      "name": "%(name)s",
      "slug": "%(slug)s",
      "creation_date": "2012-03-21 15:04:58",
      "description": "%(desc)s"
    }
  },
    {
    "model": "organization.organizationbranch",
    "pk" : "%(num)s",
    "fields": {
      "name": "%(name)s - sede",
      "info": "%(desc)s",
      "organization" : "%(num)s",
      "creation_date": "2012-03-21 15:04:58",
      "geometry": "GEOMETRYCOLLECTION (POLYGON ((%(x)s %(y)s, %(x1)s %(y1)s, %(x2)s %(y2)s, %(x)s %(y)s)))",
      "points": "MULTIPOLYGON (((%(x)s %(y)s, %(x1)s %(y1)s, %(x2)s %(y2)s, %(x)s %(y)s)))"
    }
  }""" % dict(
            num=20 + i,
            name=obj['name'],
            slug=slugify(obj['name']),
            desc=obj['description'].replace("\"", "'"),
            x=float(obj['point'][0]),
            y=float(obj['point'][1]),
            x1=float(obj['point'][0]) + 0.000001,
            y1=float(obj['point'][1]) + 0.000001,
            x2=float(obj['point'][0]) + 0.000001,
            y2=float(obj['point'][1]) - 0.000001,
            ))
        f.write(']')


def _get_val(node, name):
    try:
        return node.getElementsByTagName(name)[0].firstChild.data
    except Exception:
        return ''


def parse_kml(kml_file):
    dom = minidom.parse(kml_file)
    for node in dom.getElementsByTagName('Placemark'):
        o = {}
        o['name'] = _get_val(node, 'name')
        o['description'] = _get_val(node, 'description')
        o['point'] = _get_val(node.getElementsByTagName('Point')[0],
                              'coordinates').split(',')
        obj_list.append(o)
    generate_fixture()


def main():
    with open('doc.kml', 'r') as kml_file:
        parse_kml(kml_file)

if __name__ == '__main__':
    main()
