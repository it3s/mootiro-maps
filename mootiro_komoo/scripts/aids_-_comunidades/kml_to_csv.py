#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from xml.dom import minidom
import codecs


def sanitize(text):
    return unicode(text).replace("\"", "'").replace("\n","<br>").replace(";", ",")


def generate_csv(obj_list):
    with codecs.open('aids_-_comunidade.csv', 'w', 'utf-8') as f:
        f.write('name;description;folder;type;geometry\n')
        for o in obj_list:
            f.write('"{name}";"{description}";"{folder}";"{type}";"{geometry}"\n'.format(
                    name=sanitize(o['name']),
                    description=sanitize(o['description']),
                    folder=sanitize(o['folder']),
                    type=sanitize(o['type']),
                    geometry=sanitize(o['geometry'])
            ))


def _get_val(node, name):
    try:
        return node.getElementsByTagName(name)[0].firstChild.data
    except Exception:
        return ''


def _get_geometry(node):
    try:
        geom = _get_val(
            node.getElementsByTagName('Polygon')[0],
            'coordinates').split()
        type_ = 'polys'
    except Exception:
        try:
            geom = _get_val(
                node.getElementsByTagName('Point')[0],
                'coordinates').split()
            type_ = 'point'
        except Exception:
            geom = ''
            type_ = ''
    return type_, geom


def parse_kml(kml_file):
    dom = minidom.parse(kml_file)
    count = 0
    obj_list = []
    for folder in dom.getElementsByTagName('Folder'):
        folder = _get_val(folder, 'name')
        if '- Mapa PCU' in folder:
            for node in dom.getElementsByTagName('Placemark'):
                o = {}
                name = _get_val(node, 'name')
                geometry = _get_geometry(node)
                if geometry[0] and geometry[1]:
                    o['name'] = name
                    o['description'] = _get_val(node, 'description')
                    o['type'], o['geometry'] = geometry[0], geometry[1]
                    o['folder'] = folder
                    obj_list.append(o)
                    # print o
                    count += 1
    print '\nCount: ', count
    generate_csv(obj_list)


def main():
    with open('aids_-_comunidade.kml', 'r') as kml_file:
        parse_kml(kml_file)

if __name__ == '__main__':
    main()
