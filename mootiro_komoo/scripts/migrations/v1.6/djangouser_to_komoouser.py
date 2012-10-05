# -*- coding: utf-8 -*-
## ========= environment config ====== ##
from __future__ import unicode_literals
import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
PROJ_DIR = os.path.abspath(os.path.join(HERE, '../../../'))
SITE_ROOT = os.path.abspath(os.path.join(PROJ_DIR, '../'))
env_ = os.environ.get('KOMOO_ENV', 'dev')

sys.path.append(PROJ_DIR)
sys.path.append(SITE_ROOT)

from django.core.management import setup_environ

env_name = {
    'dev': 'development',
    'stage': 'staging',
    'prod': 'production'
}[env_]
environ = None
exec 'from settings import {} as environ'.format(env_name)
setup_environ(environ)

# ======= script ====== ##
from django.contrib.auth.models import User
from user_cas.models import KomooProfile
from komoo_user.models import KomooUser


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
#  data            |    ??? 
#

for user in User.objects.all():
    print user.id, user.get_name

    id = user.id
    name = user.get_name
    email = user.email
    # new_user.password = ??
    contact = user.get_profile().contact
    if id and name and email:
        KomooUser.objects.create(id=id, name=name, email=email, contact=contact)
    else:
        print 'Sorry but this user has missing data, and cannot be imported: '
        print ' | '.join(map(str, [id, name, email]))
