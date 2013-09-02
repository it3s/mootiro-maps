# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import simplejson as json
import sys
import codecs

models_to_be_migrated = {'komoo_resource.resource': 25, 'need.need': 20}


def parse_json_file(file_):
    new_data = {}
    with codecs.open(file_, 'r', 'utf-8') as f:
        data = json.loads(f.read())
        for entry in data:
            if entry['model'] in models_to_be_migrated.iterkeys():
                comm = entry['fields']['community']
                if comm:
                    entry['fields']['community'] = [comm]
                else:
                    entry['fields']['community'] = []

            # lets change our past ;D
            elif entry['model'] == 'reversion.version' and entry['fields']['content_type'] in models_to_be_migrated.itervalues():
                obj_data = json.loads(entry['fields']['serialized_data'])
                obj = obj_data[0]['fields']
                if not isinstance(obj['community'], list):
                    comm = obj.get('community', None)
                    obj['community'] = [comm] if comm else []
                    obj_data[0]['fields'] = obj
                    entry['fields']['serialized_data'] = json.dumps(obj_data)

        new_data = json.dumps(data)

    with codecs.open('temp.json', 'w', 'utf-8') as fileh:
        fileh.write(new_data)


def main():
    parse_json_file(sys.argv[1])


if __name__ == '__main__':
    main()
