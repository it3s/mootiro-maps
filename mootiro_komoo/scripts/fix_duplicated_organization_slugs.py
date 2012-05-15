# -*- coding: utf-8 -*-
## ========= environment config ====== ##
from __future__ import unicode_literals
import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
PROJ_DIR = os.path.abspath(os.path.join(HERE, '../'))
SITE_ROOT = os.path.abspath(os.path.join(PROJ_DIR, '../'))
env_ = 'dev'

print PROJ_DIR

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
from organization.models import Organization

os = []
for o in Organization.objects.all():
    if Organization.objects.filter(slug=o.slug).count() > 1:
        os.append(o)
        # print o.slug, ': ', o.id, ' -> ', o.name, ' => ', o.community.all()[0].name


for o in os:
    o.name = o.name + ' - ' + o.community.all()[0].name
    o.save()
    # print o.slug
