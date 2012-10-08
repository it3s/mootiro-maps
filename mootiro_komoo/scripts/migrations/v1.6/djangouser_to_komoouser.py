# # -*- coding: utf-8 -*-
# ## ========= environment config ====== ##
# from __future__ import unicode_literals
# import os
# import sys
#
# HERE = os.path.abspath(os.path.dirname(__file__))
# PROJ_DIR = os.path.abspath(os.path.join(HERE, '../../../'))
# SITE_ROOT = os.path.abspath(os.path.join(PROJ_DIR, '../'))
# env_ = os.environ.get('KOMOO_ENV', 'dev')
#
# sys.path.append(PROJ_DIR)
# sys.path.append(SITE_ROOT)
#
# from django.core.management import setup_environ
#
# env_name = {
#     'dev': 'development',
#     'stage': 'staging',
#     'prod': 'production'
# }[env_]
# environ = None
# exec 'from settings import {} as environ'.format(env_name)
# setup_environ(environ)
#
# # ======= script ====== ##
# from django.contrib.auth.models import User
# from user_cas.models import KomooProfile
# from komoo_user.models import KomooUser
# import logging
#
# logging.basicConfig(format='>> %(message)s', level=logging.DEBUG)
#
#
# ####  mappings ####
# #
# #  KomooUser       |     contrib.auth
# #  ------------------------------------
# #  id              |    preservar mesmo id
# #  name            |    user.get_name
# #  email           |    user.email
# #  password        |    CAS  (transformat para $sha1$salt$hash)
# #  contact         |    user.get_profile().contact
#
# #  LogginProviders |    social_auth
# #  ------------------------------------
# #  komoouser       |    auth.user
# #  provider        |    ??? facebook / google-oauth2
# #  email           |    ??? google -> email / facebook -> uuid
# #  data            |    ???
# #
#
# for user in User.objects.all():
#     logging.debug('%s -> %s' % (user.id, user.get_name))
#
#     id = user.id
#     name = user.get_name
#     email = user.email
#     # new_user.password = ??
#     contact = user.get_profile().contact
#     if id and name and email:
#         KomooUser.objects.get_or_create(id=id, name=name, email=email, contact=contact)
#     else:
#         logging.info('Sorry but this user has missing data, and cannot be imported: ')
#         logging.info(' | '.join(map(str, [id, name, email])))

from __future__ import unicode_literals
import simplejson as json
import sys
import codecs
import logging

logging.basicConfig(format='>> %(message)s', level=logging.DEBUG)


def convert_user(pk, fields):
    user = {}
    id = pk
    # user['name'] = ??
    email = fields.get('email', None)
    # user['contact'] = ??

    if id and email:
        return {
            'id': id,
            'email': email,
        }
    else:
        logging.info('Sorry but this user has missing data, and cannot be imported: ')
        return None

def parse_json_file(file_):
    # new_data = {}
    with codecs.open(file_, 'r', 'utf-8') as f:
        data = json.loads(f.read())
        for entry in data:
            if entry['model'] == 'auth.user':
                fields = entry['fields']
                print fields
                new_user = convert_user(entry['pk'], fields)

                if new_user:
                    pass

        # new_data = json.dumps(data)

    # with codecs.open('temp.json', 'w', 'utf-8') as fileh:
        # fileh.write(new_data)


def main():
    parse_json_file(sys.argv[1])


if __name__ == '__main__':
    main()
