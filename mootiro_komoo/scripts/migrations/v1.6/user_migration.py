# -*- coding: utf-8 -*-

####  mappings ####
#
#  KomooUser       |     contrib.auth
#  ------------------------------------
#  id              |    preservar mesmo id
#  name            |    user.get_name
#  email           |    user.email
#  password        |    CAS  (transformat para $sha1$salt$hash)
#  contact         |    user.get_profile().contact

#  LogginProviders |    social_auth
#  ------------------------------------
#  komoouser       |    auth.user
#  provider        |    ??? facebook / google-oauth2
#  email           |    ??? google -> email / facebook -> uuid
#                         (pegar email via api)
#  data            |    ???
#
from __future__ import unicode_literals
import simplejson as json
import sys
import codecs
import logging

logging.basicConfig(format='>> %(message)s', level=logging.DEBUG)


def get_profile_fields(user, data):
    for entry in data:
        if entry['model'] == 'user_cas.komooprofile' and \
           entry['fields']['user'] == user:
            return entry['fields']
    return {}


def get_full_name(fields):
    fname = fields['first_name']
    lname = fields['last_name']
    if fname or lname:
        name = '{} {}'.format(fname, lname)
        return name.strip()
    else:
        return ''


def migrate_auth_users_to_komoouser(data):
    for entry in data:
        if entry['model'] == 'auth.user':
            fields = entry['fields']

            # user convertion
            new_user = {}
            profile = get_profile_fields(entry['pk'], data)
            name = profile.get('public_name', '') or \
                   get_full_name(fields) or \
                   fields.get('username', '')
            email = fields.get('email', '')
            contact = profile.get('contact', '') or ''

            if id and name and email:
                new_user = {
                    'pk': entry['pk'],
                    'model': 'komoo_user.komoouser',
                    'fields': {
                        'name': name,
                        'email': email,
                        'contact': contact,
                        'is_active': fields['is_active'],
                        'is_admin': fields['is_superuser'],
                    }
                }
                logging.info(new_user)
            else:
                logging.info('Sorry but this user has missing data, and '
                             'cannot be imported: ')

            if new_user:
                data.append(new_user)
    return data


def migrate_profile_from_usercas_to_komoouser(data):
    for entry in data:
        if entry['model'] == 'user_cas.komooprofile':
            entry['model'] = 'komoo_user.komooprofile'
    return data


def migrate_mootiro_profile_users_to_komoo_users():
    '''
        Usa a seguinte estratégia para
    '''
    import psycopg2
    import csv
    import json

    db_user = 'it3s_andre'
    db_pass = '1234'
    conn_string = "host='localhost' dbname='mootiro_profile' user='%s' password='%s'" % (db_user, db_pass)
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    file_path = '/tmp/mootiro_profile_user.csv'
    query = '''COPY (SELECT * FROM "user") TO '%s' WITH (FORMAT CSV, HEADER TRUE);''' % file_path
    cursor.execute(query)

    f = open(file_path, 'r' )
    reader = csv.DictReader(f)
    out = json.dumps([row for row in reader])
    print out


def parse_json_file(file_):
    new_data = {}
    with codecs.open(file_, 'r', 'utf-8') as f:
        data = json.loads(f.read())
        data = migrate_auth_users_to_komoouser(data)
        data = migrate_profile_from_usercas_to_komoouser(data)

        new_data = json.dumps(data)

    with codecs.open('temp.json', 'w', 'utf-8') as f_:
        f_.write(new_data)


def main():
    parse_json_file(sys.argv[1])


if __name__ == '__main__':
    main()
