#! /usr/bin/env python
# -*- coding: utf-8 -*-

## ========= environment config ====== ##
from __future__ import unicode_literals
import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
PROJ_DIR = os.path.abspath(os.path.join(HERE, '../..'))
SITE_ROOT = os.path.abspath(os.path.join(PROJ_DIR, '../..'))

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

## ======= script ====== ##
import codecs
from django.contrib.auth.models import User
from datetime import datetime
from organization.models import Organization
from community.models import Community

elaste = User.objects.get(username='elaste')
jacarei = Community.objects.get(name='Jacareí')

def save_obj(vals):
    tipo, name, endereco, contato = vals
    contact = "{}\n{}".format(endereco, contato)

    o = Organization()

    o.name = name.title().replace('Emei', 'EMEI').replace('Emef', 'EMEF'
        ).replace('Ee', 'EE')
    o.contact = contact
    o.description = ''

    o.creator = elaste
    o.creation_date = datetime.now()

    o.save()
    for t in [tipo, 'Jacareí']:
        o.tags.add(t)

    o.community.add(jacarei)


with codecs.open(
        'scripts/jacarei/jacarei_escolas.csv', 'r', 'utf-8') as f:

    f.readline()  # consume first line
    for line in f:
        save_obj(line.split(';'))

