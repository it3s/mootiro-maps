# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import simplejson as json
import sys
import codecs


def migrate_importsheet(data):
    for entry in data[::]:
        if entry['model'] == 'importsheet.importsheet':
            fields = entry['fields']

            entry['kml_import'] = False

    return data


def parse_json_file(file_):
    new_data = {}
    with codecs.open(file_, 'r', 'utf-8') as f:
        data = json.loads(f.read())
        data = migrate_importsheet(data)

        new_data = json.dumps(data)

    with codecs.open('temp.json', 'w', 'utf-8') as f_:
        f_.write(new_data)


def main():
    parse_json_file(sys.argv[1])


if __name__ == '__main__':
    main()
