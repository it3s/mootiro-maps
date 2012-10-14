# -*- coding: utf-8 -*-

####  mappings ####
#
#  User            |     contrib.auth
#  ------------------------------------
#  id              |    preservar mesmo id
#  name            |    user.get_name
#  email           |    user.email
#  password        |    CAS  (transformat para $sha1$salt$hash)
#  contact         |    user.get_profile().contact

#  LogginProviders |    social_auth
#  ------------------------------------
#  user            |    auth.user
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
import csv

logging.basicConfig(format='>> %(message)s', level=logging.DEBUG)


def get_profile_fields(user, data):
    for entry in data:
        if entry['model'] == 'user_cas.komooprofile' and \
           int(entry['fields']['user']) == int(user):
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


def get_user_email(pk, data):
    for entry in data:
        if entry['model'] == 'komoo_user.user' and entry['pk'] == pk:
            return entry['fields']['email']
    else:
        return ''


def remove_deprecated_tables(data):
    logging.info('Removing deprecated tables (sites, comment, komooprofile)')
    for entry in data[::]:
        if entry['model'] == 'sites.site' or \
           entry['model'] == 'comments.comment' or \
           entry['model'] == 'comments.commentflag' or \
           entry['model'] == 'user_cas.komooprofile':
            data.remove(entry)
    return data


def migrate_auth_users_to_user(data):
    logging.info('migrating contrib.auth.User to komoo_user.User')
    for entry in data[::]:
        if entry['model'] == 'auth.user':
            fields = entry['fields']

            # user convertion
            new_user = {}
            profile = get_profile_fields(int(entry['pk']), data)
            name = profile.get('public_name', '') or \
                   get_full_name(fields) or \
                   fields.get('username', '')
            # dont know what to do when dont have an email
            email = fields.get('email', '') or '%s@email.com' % entry['pk']

            contact = profile.get('contact', '')
            if contact is None:
                contact = ''

            if id and name and email:
                new_user = {
                    'pk': entry['pk'],
                    'model': 'komoo_user.user',
                    'fields': {
                        'name': name,
                        'email': email,
                        'contact': contact,
                        'points': profile.get('points', None),
                        'lines': profile.get('lines', None),
                        'polys': profile.get('polys', None),
                        'geometry': profile.get('geometry', None),
                        'is_active': fields['is_active'],
                        'is_admin': fields['is_superuser'],
                    }
                }
                # logging.info(new_user)
            else:
                logging.info('Sorry but this user has missing data, and '
                             'cannot be imported: ')

            if new_user:
                data.append(new_user)
    return data


def migrate_login_providers(data):
    logging.info('Migrating Logging Provides')
    seq = 0
    for entry in data[::]:
        if entry['model'] == 'social_auth.usersocialauth':
            fields = entry['fields']

            if 'google-oauth2' == fields['provider']:
                provider = fields['provider']
                email = fields['uid']
            else:
                provider = 'facebook-oauth2'
                email = get_user_email(fields['user'], data)

            seq += 1

            credentials = {
                'pk': seq,
                'model': 'login_providers.externalcredentials',
                'fields': {
                    'user': fields['user'],
                    'provider': provider,
                    'email': email,
                    'data': fields['extra_data'],
                }
            }

            data.remove(entry)
            data.append(credentials)

    return data


def migrate_mootiro_profile_users_to_komoo_users(data):
    logging.info('Migrating mootiro profile passwords')
    # db_user, db_pass = ('mootiro_profile', '.Pr0f1l3.')
    file_path = '/tmp/mootiro_profile_users.csv'

    # conn_string = "host='localhost' dbname='mootiro_profile' user='%s' password='%s'" % (db_user, db_pass)
    # conn = psycopg2.connect(conn_string)
    # cursor = conn.cursor()
    # query = '''COPY (SELECT * FROM "user") TO '%s' WITH (FORMAT CSV, HEADER TRUE);''' % file_path
    # cursor.execute(query)

    f = open(file_path, 'r')
    reader = csv.DictReader(f)

    for row in reader:
        email = row['email']
        password_hash = row['password_hash']

        if password_hash.startswith('sha1$'):
            password_hash = password_hash[5:]

        for entry in data:
            fields = entry['fields']
            if entry['model'] == 'komoo_user.user' and \
               fields['email'] == email:

                if password_hash == '!':
                    logging.info('User with email {} has no password!'.format(
                                    email))

                fields['password'] = password_hash

    return data


def remove_votes(data):
    logging.info('Removing Vote app entries')
    for entry in data[::]:
        if entry['model'].startswith('vote.'):
            data.remove(entry)
        elif 'votes_down' in entry['fields']:
            idx = data.index(entry)
            d = data[idx]['fields']
            del d['votes_up']
            del d['votes_down']
    return data


def parse_json_file(file_):
    new_data = {}
    with codecs.open(file_, 'r', 'utf-8') as f:
        data = json.loads(f.read())
        data = migrate_auth_users_to_user(data)
        data = migrate_login_providers(data)
        data = migrate_mootiro_profile_users_to_komoo_users(data)

        data = remove_deprecated_tables(data)
        data = remove_votes(data)

        new_data = json.dumps(data)

    with codecs.open('temp.json', 'w', 'utf-8') as f_:
        f_.write(new_data)


def main():
    parse_json_file(sys.argv[1])


if __name__ == '__main__':
    main()
