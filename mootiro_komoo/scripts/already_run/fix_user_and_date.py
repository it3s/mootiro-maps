## ========= environment config ====== ##
from __future__ import unicode_literals
import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
PROJ_DIR = os.path.abspath(os.path.join(HERE, '../'))
SITE_ROOT = os.path.abspath(os.path.join(PROJ_DIR, '../'))

env_ = os.environ.get('KOMOO_ENV', 'dev')

sys.path.append(PROJ_DIR)
sys.path.append(SITE_ROOT)

from django.core.management import setup_environ

env_name = ['', 'development', 'staging', 'production'][\
            3 * (int(env_ == 'prod')) +\
            2 * (int(env_ == 'stage')) +\
                (int(env_ == 'dev'))]
environ = None
exec 'from settings import {} as environ'.format(env_name)
setup_environ(environ)

# ======= script ====== ##
from django.contrib.auth.models import User
from datetime import datetime
from komoo_resource.models import Resource
from need.models import Need
from organization.models import Organization, OrganizationBranch

elaste = User.objects.get(username='elaste')

for model in [Resource, Need, Organization, OrganizationBranch]:
    for obj in model.objects.all():
        changed = False
        now = datetime.now()
        if not obj.creator:
            obj.creator = elaste
            changed = True
        if not obj.creation_date:
            obj.creation_date = now
            changed = True
        if changed:
            obj.save()
