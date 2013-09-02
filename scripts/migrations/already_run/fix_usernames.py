#! /usr/bin/env python
# -*- coding: utf-8 -*-

## ========= environment config ====== ##
from __future__ import unicode_literals
import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
PROJ_DIR = os.path.abspath(os.path.join(HERE, '..'))
SITE_ROOT = os.path.abspath(os.path.join(PROJ_DIR, '..'))

env_ = os.environ.get('KOMOO_ENV', 'dev')

sys.path.append(PROJ_DIR)
sys.path.append(SITE_ROOT)

from django.core.management import setup_environ

env_name = ['', 'development', 'staging', 'production'][
            3 * (int(env_ == 'prod')) +
            2 * (int(env_ == 'stage')) +
                (int(env_ == 'dev'))]
environ = None
exec 'from settings import {} as environ'.format(env_name)
setup_environ(environ)

## ======= script ====== ##
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

for u in User.objects.all():
    slug = slugify(u.username).replace('-', '_')
    while User.objects.filter(username=slug).count() and \
          User.objects.filter(username=slug)[0] != u:
        slug += '_'
    u.username = slug
    u.save()

