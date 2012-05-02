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
from organization.models import Organization, OrganizationCategory
from django.contrib.auth.models import User
from datetime import datetime


# build field index
alpha = 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z'.split()
field_index = alpha[:]
for a  in ['A', 'B']:
    for b in alpha:
        if not (a + b) in ['BX', 'BY', 'BZ']:
            field_index.append(a + b)
field_index = {k: i for i, k in enumerate(field_index)}


def get_field(vals, field):
    return vals[field_index[field]]


def desc_localization(vals):
    return """
### Localização:


{R} fica no distrito de {J} na cidade de São Paulo. Pertence à Delegacia do Ensino {H}.

""".format(R=get_field(vals, 'R'),
           J=get_field(vals, 'J'),
           H=get_field(vals, 'H'))


def desc_atendimento(vals):
    mapper_fields = [
        ('Creche', 'BA', 'AK'),
        ('Pré-Escola', 'BB', 'AL'),
        ('1ª a 4ª série', 'BE', 'AM'),
        ('5ª a 8ª série', 'BF', 'AN'),
        ('Ensino Médio', 'BN', 'AQ'),
        ('Ensino Profissionalizante', 'BP', 'AS'),
        ('Ensino Especial', 'BO', 'AR'),
        ('Educação de Jovens e Adultos (1ª a 4ª série)', 'BQ', 'AT'),
        ('Educação de Jovens e Adultos (5ª a 8ª série)', 'BR', 'AU'),
        ('Educação de Jovens e Adultos (Ensino Médio)', 'BS', 'AV'),
    ]
    st = ''
    atendimento_header = False

    for i, mapper in enumerate(mapper_fields):
        if int(get_field(vals, mapper[1])):
            st += """
- **{tipo}**: {num_cl} classes com {num_al} alunos
""".format(tipo=mapper[0], num_cl=get_field(vals, mapper[1]),
           num_al=get_field(vals, mapper[2]))
    if st:
        st = """
### Atendimento:

""" + st
    return st


def desc_contato(vals):
    contato = """
{V}, {W}
{Y}, São Paulo-SP, CEP: {Z}-{AA}
""".format(V=get_field(vals, 'V').rstrip().title(), W=get_field(vals, 'W'),
           Y=get_field(vals, 'Y').rstrip().title(), Z=get_field(vals, 'Z'),
           AA=get_field(vals, 'AA'),
    )
    f1 = get_field(vals, 'AE').strip()
    f2 = get_field(vals, 'AF').strip()
    fax = get_field(vals, 'AG').strip()

    fones = '\n'
    if f1:
        fones += 'Fone: (11) {}-{}  \n'.format(f1[:4], f1[4:])
    if f2:
        fones += 'Fone: (11) {}-{}  \n'.format(f2[:4], f2[4:])
    if fax:
        fones += 'Fax: (11) {}-{}  \n'.format(fax[:4], fax[4:])

    return contato + fones + '\n'


category_id = OrganizationCategory.objects.get(name='Education').id


def save_obj(vals):
    # prepare data
    nome = ' '.join([
        get_field(vals, 'S'),
        get_field(vals, 'T').title(),
        get_field(vals, 'U').title()
    ])

    desc = desc_localization(vals)
    desc += desc_atendimento(vals)

    tags = ['Escola', get_field(vals, 'S'), get_field(vals, 'H').title(),
             get_field(vals, 'J').title()]

    contato = desc_contato(vals)
    user = User.objects.get(username='elaste')
    now = datetime.now()

    # save data
    o = Organization()
    o.name = nome
    o.description = desc
    o.contact = contato
    o.creator = user
    o.creation_date = now
    o.save()

    # save m2m relations
    o.categories.add(category_id)
    for tag in tags:
        o.tags.add(tag)


with codecs.open(
        'scripts/escolas/Escolas_municipais_SP.csv', 'r', 'utf-8') as f:

    # consume first 2 lines
    f.readline()
    f.readline()

    count = 0
    for l in f:
        line = l
        # print line
        vals = line.split(';')

        if get_field(vals, 'A') == 'sim':
            # print_hit(line, vals)
            count += 1
            save_obj(vals)

    print 'count', count
