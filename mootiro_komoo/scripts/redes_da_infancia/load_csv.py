#! /usr/bin/env python
# -*- coding: utf-8 -*-

## ========= environment config ====== ##
from __future__ import unicode_literals
import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
PROJ_DIR = os.path.abspath(os.path.join(HERE, '../..'))
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
import unicodecsv
from django.contrib.auth.models import User
from datetime import datetime
from organization.models import OrganizationCategoryTranslation, Organization
from need.models import TargetAudience
from komoo_resource.models import Resource
from komoo_project.models import Project, ProjectRelatedObject

users = {
    'AS': User.objects.get(username='anapaulabrasa'),
    'AP': User.objects.get(username='anapaulabrasa'),
    'CL': User.objects.get(username='cicalessa'),
    'OF': User.objects.get(username='olga'),
}

projeto = Project.objects.get(name="Redes de Promoção dos Direitos da Criança e do Adolescente")


# build field index
alpha = 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z'.split()
field_index = alpha[:]
for pre in ['A', 'B']:
    for b in alpha:
        if (pre + b) == 'BO':
            break
        else:
            field_index.append(pre + b)
field_index = {k: i for i, k in enumerate(field_index)}


def get_field(vals, field):
    return vals[field_index[field]]

count = 0


def format_fields(vals, *args):
    fmt = {}
    for arg in args:
        fmt[arg] = get_field(vals, arg)
    return fmt


def save_org(vals):
    if not get_field(vals, 'A') and not get_field(vals, 'B'):
        return

    name = "{} - {}".format(
            get_field(vals, 'B').title(), get_field(vals, 'A'))
    name = name.strip()

    desc = """
####Atuação

####Localização

A {B} fica localizada em {AJ}, {AW}.


####Estrutura e Dirigentes

- {AZ}


####Registro e Certificações

**CNPJ:** {AX}


####Comunicação

- **Facebook:** [{BD}] ({BE} "{B} no Facebook")
- **Blogue:** [{B}] ({BF} "Blogue da {B}")


####Participações e Representações

""".format(**format_fields(vals, 'B', 'AJ', 'AW', 'AZ', 'AX', 'BD', 'BE', 'BF'))

    if get_field(vals, 'P'):
        desc += """
- [{P}] (http://maps.mootiro.org/organization/comite-nacional-de-enfrentamento-a-violencia-sexual-contra-criancas-e-adolescentes "Comitê Nacional no Mootiro Maps"): {BA}, {BB}
""".format(**format_fields(vals, 'P', 'BA', 'BB'))

    if get_field(vals, 'K'):
        desc += """
- [{K}] (http://maps.mootiro.org/organization/rede-andi-brasil "Rede ANDI Brasil no MootiroMaps")
""".format(**format_fields(vals, 'K'))

    if get_field(vals, 'L'):
        desc += """
- [{L}] (http://maps.mootiro.org/organization/rnpi-rede-nacional-primeira-infancia "Rede Nacional Primeira Infância no MootiroMaps")
""".format(**format_fields(vals, 'L'))

    desc += """

#### Referências

- [{BM}] ({BL} "Arquivo no GoogleDocs"), {BN}
- [Site institucional da {B}] ({Y} "")

    """.format(**format_fields(vals, 'BM', 'BN', 'BL', 'B', 'Y'))

    link = get_field(vals, 'Y')

    contact = """
{AE}, {AF}, {AG}
{AH}, CEP: {AI}
{AJ} - {AK}

**Fone:** ({AB}) {AC} - {AA}

**E-mail:** {Z}

    """.format(**format_fields(vals, 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK',
                             'AB', 'AC', 'AA', 'Z'))

    cat = "Promoção de direitos humanos"
    cat = OrganizationCategoryTranslation.objects.filter(name__icontains=cat)
    if cat.count():
        categoria = cat[0].category

    tags = [get_field(vals, f) for f in
            ['AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW']]

    # Público-Alvo
    public = [get_field(vals, f) for f in ['AM', 'AN', 'AO', 'AP']]

    now = datetime.now()

    o = Organization()
    o.name = name
    o.description = desc
    o.contact = contact
    o.link = link
    o.category = categoria
    o.creation_date = now
    o.creator = users[get_field(vals, 'C')]
    o.save()
    for t in tags:
        o.tags.add(t)
    for p in public:
        p, c = TargetAudience.objects.get_or_create(name=p)
        o.target_audiences.add(p)

    ProjectRelatedObject.objects.create(project=projeto, content_object=o)
    print 'OK  -  ', name


def save_resource(vals):
    name = get_field(vals, 'B').title().strip()

    if not name:
        return

    desc = """

#### Representante

O {AS} do [Comitê Nacional de Enfrentamento à Violência Sexual contra Crianças e Adolescentes](http://maps.mootiro.org/organization/comite-nacional-de-enfrentamento-a-violencia-sexual-contra-criancas-e-adolescentes "Comitê Nacional no MootiroMaps") no estado de {AW}, é representado por {AA}.

{AA} integra a organização {BG} - {BH}.

#### Referências

- [{BM}] ({BL} "Arquivo no GoogleDocs"), {BN}
- [Site institucional do Comitê Nacional de Enfrentamento à Violência Sexual contra Crianças e Adolescentes] (http://www.comitenacional.org.br/ "")


    """.format(**format_fields(vals, 'AS', 'AW', 'AA', 'BG', 'BH', 'BM', 'BL', 'BN'))

    contact = """

**Fone:** ({AB}) {AC}

**E-mail:** {Z}

**Facebook:** [{BD}] ({BE} "{B} no Facebook")

    """.format(**format_fields(vals, 'AB', 'AC', 'Z', 'BD', 'BE', 'B'))

    tags = [get_field(vals, f) for f in
            ["AQ", "AR", "AS", "AT", "AU", "AV", "AW"]]

    now = datetime.now()

    o = Resource()
    o.name = name
    o.description = desc
    o.contact = contact
    o.creation_date = now
    o.creator = users[get_field(vals, 'C')]
    o.save()
    for t in tags:
        o.tags.add(t)

    ProjectRelatedObject.objects.create(project=projeto, content_object=o)
    print 'OK  -  ', name


def save_obj(vals):
    global count
    if get_field(vals, 'J') == 'sim':
        if get_field(vals, 'I') == 'R':
            save_resource(vals)
        elif get_field(vals, 'I') == 'O':
            save_org(vals)
        count += 1

fname = 'scripts/redes_da_infancia/dados.csv'
rows = unicodecsv.reader(open(fname), encoding='utf-8')

for row in rows:
    save_obj(row)

print 'count: ', count


