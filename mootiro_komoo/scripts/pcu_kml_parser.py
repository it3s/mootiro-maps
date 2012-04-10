#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from xml.dom import minidom
import csv
import codecs
import cStringIO


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def generate_csv(obj_list):
    with codecs.open('pcu_csv.csv', 'w', 'utf-8') as f:
        writer = UnicodeWriter(f)
        writer.writerow(('name', 'description', 'folder', 'type', 'geometry'))
        # f.write('name,description,folder,type,geometry\n')
        for o in obj_list:
            # f.write('"{name}","{description}","{folder}","{type}","{geometry}"\n'.format(
            #     name=unicode(o.get('name', '')),
            #     description=unicode(o.get('description', '')),
            #     folder=unicode(o.get('folder', '')),
            #     type=unicode(o.get('type', '')),
            #     geometry=unicode(o.get('geometry', '')).decode('utf-8')
            # ))
            writer.writerow((
                unicode(o['name']),
                unicode(o['description']),
                unicode(o['folder']),
                unicode(o['type']),
                unicode(o['geometry'])
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
        for node in dom.getElementsByTagName('Placemark'):
            o = {}
            name = _get_val(node, 'name')
            geometry = _get_geometry(node)
            if name and geometry[0] and geometry[1]:
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
    with open('pcu_doc.kml', 'r') as kml_file:
        parse_kml(kml_file)

if __name__ == '__main__':
    main()
