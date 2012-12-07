# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import simplejson as json

from django.template import Context, Template
from django.utils.translation import ugettext as _
from django.contrib.gis.gdal.error import OGRException

from main.models import GeoRefModel
from authentication.models import User
from community.models import Community


def set_controle(obj):
    # obj.object_dict['id'] = obj.row_dict['Controle']['ID']
    try:
        obj.object_dict['creator'] = User.objects \
                .get(id=obj.row_dict['Controle']['ID do mapeador'])
    except:
        msg = 'ID do mapeador inválido: {} não pertence a nenhum usuário.' \
                    .format(obj.row_dict['Controle']['ID do mapeador'])
        obj.errors.append(msg)


def set_nome(obj):
    if obj.row_dict['Nome']['Sigla'] and \
       obj.row_dict['Nome']['Nome da organização']:
        obj.object_dict['name'] = '{} - {}' \
                .format(obj.row_dict['Nome']['Nome da organização'],
                        obj.row_dict['Nome']['Sigla'])
    else:
        obj.object_dict['name'] = obj.row_dict['Nome']['Nome da organização']


def set_contato(obj):
    contact = obj.row_dict['Contato']
    c = Context({
        'address': contact['Endereço'],
        'number': contact['Número'],
        'complement': contact['Complemento'],
        'district': contact['Bairro'],
        'zipcode': contact['CEP'],
        'city': contact['Município'],
        'state': contact['UF'],
        'area_code': contact['DDD'],
        'phone_number': contact['Telefone'],
        'email': contact['E-mail'],
    })
    t = Template('''
{% if address %}**Endereço:** {{address}}, {{number}}{% if complement %}, {{complement}}{% endif %} - {{district}}
{% if zipcode %}CEP: {{zipcode}}, {% endif %}{{city}}/{{state}}{% endif %}

{% if phone_number %}**Telefone:** {% if area_code %}({{area_code}}){% endif %} {{phone_number}}{% endif %}

{% if email %}**E-mail:** {{email}}{% endif %}
''')
    obj.object_dict['contact'] = t.render(c)


def set_descricao(obj):
    sections = obj.row_dict['Descrição']
    # filter empty sections
    for title in sections:  # do not use dict comprehension
        if not sections[title]:
            sections.pop(title)

    # clean and map references dicts
    refs = [v for k, v in obj.row_dict.items() if k.startswith('Referência')]
    refs = filter(lambda r: bool([v for v in r.values() if v]), refs)
    refs = map(lambda ref: dict(author=ref['Autor'], source=ref['Fonte'], 
            link=ref['Link'], link_title=ref['Título do link'], date=ref['Data']), refs)

    c = Context({
        'sections': sections,
        'references': refs,
    })
    t = Template('''\
{% for title, text in sections.items %}
{% if text %}#### {{ title }}
{{ text|safe }}{% endif %}
{% endfor %}
{% if references %}#### Referências{% endif %}
{% for r in references %}\
 - {% if r.author %}{{r.author}}: {% endif %}{% if r.link %}[{{r.source}}]({{r.link}} "{{r.link_title}}"){% endif %}{% if r.date %}, consultado em {{r.date}}{% endif %}
{% endfor%}\
''')
    obj.object_dict['description'] = t.render(c)


def set_comunidades(obj):
    communities = []
    for cid in [c for c in obj.row_dict['Comunidades'].values() if c]:
        q = Community.objects.filter(id=cid)
        if q.exists():
            communities.append(q.get())
        else:
            msg = 'ID de comunidade inválido: {0}'.format(cid)
            obj.errors.append(msg)
    obj.object_dict['community'] = communities


def set_coordenadas_ponto(obj):
    gd = obj.row_dict['Geometria']
    point = gd['Ponto']
    point_as_area = gd['Ponto como área']
    # polygons = [gd[k] for k in gd.keys() if k.startswith('Polígono') and gd[k]]
    polygons = None

    num_geometries = len([v for v in [point, point_as_area, polygons] if v])
    if num_geometries == 0:
        return  # nothing to do!
    if num_geometries > 1:
        msg = 'Mais de uma geometria definida. Defina somente a coluna "Ponto",'\
              'ou "Ponto como Área", ou "Polígono 1 Polígono 2, ..."'
        obj.errors.append(msg)

    geodict = {
        'type': 'GeometryCollection',
        'geometries': []
    }

    try:
        if point:
            # FIXME: correct order is lat, lng. Before fixing must adjust the
            #        both in DB and in the map.
            lng, lat = point.split(',')
            lat, lng = float(lat), float(lng)
            coords = [[lat, lng]]
            geodict['geometries'] = [{
                'type': 'MultiPoint',
                'coordinates': coords
            }]
        elif point_as_area:
            dt = 0.0005
            lat, lng = point_as_area.split(',')
            lat, lng = float(lat), float(lng)
            # FIXME: correct order is lat, lng. Before fixing must adjust the
            #        both in DB and in the map.
            aux = lng
            lng = lat
            lat = aux
            coords = [[[lat+dt, lng+dt], [lat+dt, lng-dt],
                       [lat-dt, lng-dt], [lat-dt, lng+dt],
                       [lat+dt, lng+dt]]]  # closes polygon
            geodict['geometries'] = [{
                'type': 'Polygon',
                'coordinates': coords
            }]
        elif polygons:
            # list of polygons, each polygon is a list of points
            coords = []
            for poly_str in polygons:
                points = poly_str.split(' ')
                points = [p.split(',') for p in points]
                # FIXME: correct order is lat, lng. Before fixing must adjust the
                #        both in DB and map
                points = [[float(lat), float(lng)] for lng, lat in points]
                coords.append(points)

            geodict['geometries'] = [{
                'type': 'Polygon',
                'coordinates': coords
            }]
            
        g = GeoRefModel()
        obj.object_dict['geometry'] = json.dumps(geodict)
        g.geometry = obj.object_dict['geometry']

    except ValueError:
        msg = 'Dado de geometria não é um número válido.'
        obj.errors.append(msg)

    except OGRException:
        msg = 'Má formação da(s) coluna(s) de geometria.'
        obj.errors.append(msg)


def set_tags(obj):
    obj.object_dict['tags'] = filter(bool, obj.row_dict['Palavras-chave'].values())
    # TODO: put similar tags in the warnings dict

    # Data qualification tags
    if not obj.row_dict['Contato']['CEP']:
        obj.object_dict['tags'].append('sem CEP')
    if not obj.row_dict['Contato']['Telefone']:
        obj.object_dict['tags'].append('sem telefone')
    if not obj.row_dict['Contato']['E-mail']:
        obj.object_dict['tags'].append('sem e-mail')
    if not bool([s for s in obj.row_dict['Geometria'].values() if s != '']):
        obj.object_dict['tags'].append('sem ponto')
