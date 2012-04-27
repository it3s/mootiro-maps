#! /usr/bin/env python
# -*- coding: utf-8 -*-

## ========= environment config ====== ##
from __future__ import unicode_literals
import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
PROJ_DIR = os.path.abspath(os.path.join(HERE, '../..'))
SITE_ROOT = os.path.abspath(os.path.join(PROJ_DIR, '../..'))
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

## ======= script ====== ##
import codecs
from organization.models import Organization, OrganizationBranch
from need.models import Need
from komoo_resource.models import Resource
from community.models import Community
from datetime import datetime
from django.contrib.auth.models import User


def print_hit(line, vals):
    print '\n---------------------------------'
    print 'line:'
    print line
    print 're split:'
    print vals


def save_obj(vals):
    imp, transf, comunidade, name, desc, folder, tipo, geom = vals
    geom = eval(geom)
    print 'saving: ', vals

    user = User.objects.get(username='elaste')
    now = datetime.now()

    # Transform geometry data type
    if transf == 'sim':
        tipo = 'polys'
        x, y, z = map(float, geom[0].split(','))
        geom = []
        geom.append('%s,%s,%s' % (x + 0.0003, y + 0.0003, z))
        geom.append('%s,%s,%s' % (x + 0.0003, y - 0.0003, z))
        geom.append('%s,%s,%s' % (x - 0.0003, y - 0.0003, z))
        geom.append('%s,%s,%s' % (x - 0.0003, y + 0.0003, z))
        geom.append('%s,%s,%s' % (x + 0.0003, y + 0.0003, z))

    # build geomtry info
    if tipo == 'polys':
        coords = ''
        for i, coord in enumerate(geom):
            x, y, z = coord.split(',')
            coords += '%s %s' % (y, x)
            if not i == len(geom) - 1:
                coords += ', '
        geo_ref = 'GEOMETRYCOLLECTION ( POLYGON (( %s )))' % coords
    elif tipo == 'point':
        x, y, z = geom[0].split(',')
        geo_ref = 'GEOMETRYCOLLECTION ( POINT ( %s %s))' % (y, x)

    # save Resource
    if imp == 'R':

        #fix comunidade
        tags = []
        if ',' in comunidade:
            split = [c.strip() for c in comunidade.split(',')]
            comunidade, tags = split[0], split[1:]

        r = Resource()
        r.name = name
        r.description = desc

        # comunity is the firt
        if comunidade:
            c = Community.objects.get(slug=comunidade)
            r.community = c

        r.creator = user
        r.creation_date = now
        r.geometry = geo_ref
        r.save()

        # load remaining comunities as tags
        for tag in tags:
            r.tags.add(tag)

    # save Need
    elif imp == 'N':

        #fix comunidade
        tags = []
        if ',' in comunidade:
            split = [c.strip() for c in comunidade.split(',')]
            comunidade, tags = split[0], split[1:]

        n = Need()
        n.title = name
        n.description = desc

        if comunidade:
            c = Community.objects.get(slug=comunidade)
            n.community = c

        n.creator = user
        n.creation_date = now
        n.geometry = geo_ref
        # n.target_audiences.add(1)
        n.save()

        # load remaining comunities as tags
        for tag in tags:
            n.tags.add(tag)

    # save organization
    elif imp == 'O':
        if name:
            o = Organization()
            o.name = name
            o.description = desc
            o.creation_date = now
            o.creator = user
            o.save()
            for comm in [c.strip() for c in comunidade.split(',')]:
                c = Community.objects.get(slug=comm)
                o.community.add(c)

            b = OrganizationBranch()
            b.name = name + ' - sede'
            b.geometry = geo_ref
            b.organization = o
            b.creator = user
            b.creation_date = now
            b.save()


with codecs.open('scripts/uberlandia/ceps.csv',
                 'r', 'utf-8') as f:
    # consume first line
    f.readline()

    count = {'O': 0, 'N': 0, 'R': 0}
    for l in f:
        line = l
        print line
        vals = line.split(';')
        imp, tranf, comunidade, name, desc, folder, tipo, geom = vals
        if imp in ['O', 'N', 'R']:
            print_hit(line, vals)
            count[imp] += 1
            save_obj(vals)

    print 'count', count
