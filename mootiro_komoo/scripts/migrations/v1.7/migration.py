# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import simplejson as json
import sys
import codecs
import logging
import csv

logging.basicConfig(format='>> %(message)s', level=logging.DEBUG)


def migrate_resources(data):
    logging.info('Migrating Resources')

    for entry in data:
        if entry['model'] == 'komoo_resource.resource':
            entry['model'] = 'resources.resource'
        elif entry['model'] == 'komoo_resource.resourcekind':
            entry['model'] = 'resources.resourcekind'
    return data


def migrate_projects(data):
    logging.info('Migrating Projects')

    for entry in data:
        if entry['model'] == 'komoo_project.projects':
            entry['model'] = 'projects.project'
        elif entry['model'] == 'komoo_project.projectrelatedobject':
            entry['model'] = 'projects.projectrelatedobject'
    return data


def parse_json_file(file_):
    new_data = {}
    with codecs.open(file_, 'r', 'utf-8') as f:
        data = json.loads(f.read())

        data = migrate_resources(data)
        data = migrate_projects(data)

        new_data = json.dumps(data)

    with codecs.open('temp.json', 'w', 'utf-8') as f_:
        f_.write(new_data)


def main():
    parse_json_file(sys.argv[1])


if __name__ == '__main__':
    main()
