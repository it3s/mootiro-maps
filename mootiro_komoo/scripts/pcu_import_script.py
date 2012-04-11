#! /usr/bin/env python
# -*- coding: utf-8 -*-

## ========= environment config ====== ##
from __future__ import unicode_literals
import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
PROJ_DIR = os.path.abspath(os.path.join(HERE, '..'))
SITE_ROOT = os.path.abspath(os.path.join(PROJ_DIR, '..'))
env_ = 'dev'

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
import re
from organization.models import Organization, OrganizationBranch
from need.models import Need
from komoo_resource.models import Resource
from community.models import Community


def print_hit(line, vals):
    print '\n---------------------------------'
    print 'line:'
    print line
    print 're split:'
    print vals


def save_obj(vals):
    imp, transf, comunidade, name, desc, folder, tipo, geom, junk = vals
    geom = eval(geom)
    print type(geom)
    print 'saving: ', vals
    if transf == 'sim':
        tipo = 'polys'
        x,y, z = map(float, geom[0].split(','))
        geom = []
        geom.append('%s,%s,%s' % (x + 0.0005, y + 0.0005, z))
        geom.append('%s,%s,%s' % (x + 0.0005, y - 0.0005, z))
        geom.append('%s,%s,%s' % (x - 0.0005, y - 0.0005, z))
        geom.append('%s,%s,%s' % (x - 0.0005, y + 0.0005, z))
        geom.append('%s,%s,%s' % (x + 0.0005, y + 0.0005, z))

    if tipo == 'polys':
        coords = ''
        for i, coord in enumerate(geom):
            x,y, z = coord.split(',')
            coords += '%s %s' % (y, x)
            if not i == len(geom) - 1:
                coords += ', '
        geo_ref = 'GEOMETRYCOLLECTION ( POLYGON (( %s )))' % coords
    elif tipo == 'point':
        x,y, z = geom[0].split(',')
        geo_ref = 'GEOMETRYCOLLECTION ( POINT ( %s %s))' % (y, x)


    print geo_ref
    if imp == 'R':
        r = Resource()
        r.name = name
        r.description = desc
        if comunidade:
            c = Community.objects.get(slug=comunidade)
            r.community = c
        r.geometry = geo_ref
        r.save()

    elif imp == 'N':
        n = Need()
        n.title = name
        n.description = desc
        if comunidade:
            c = Community.objects.get(slug=comunidade)
            n.community = c
        n.geometry = geo_ref
        n.target_audiences.add(1)
        n.save()

    elif imp == 'O':
        if name:
            o = Organization()
            o.name = name
            o.description = desc
            o.save()
            if comunidade:
                c = Community.objects.get(slug=comunidade)
                o.community.add(c)

            b = OrganizationBranch()
            b.name = name + ' - sede'
            b.geometry = geo_ref
            b.organization = o
            b.save()








with codecs.open('scripts/pcu_importacao.csv', 'r', 'utf-8') as f:
    # consume first line
    f.readline()

    buff = ''
    count = 0
    for l in f:
        line = buff + l
        vals = re.split(''';(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', line)
        if len(vals) < 9:
            buff = line
            continue
        else:
            buff = ''
            imp, tranf, comunidade, name, desc, folder, tipo, geom, junk = vals
            if imp in ['O', 'N', 'R']:
                # print_hit(line, vals)
                save_obj(vals)
                count += 1

    print 'count', count
