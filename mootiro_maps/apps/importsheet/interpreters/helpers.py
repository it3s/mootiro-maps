# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import simplejson as json

from django.template import Context, Template
from django.utils.translation import ugettext as _
from django.contrib.gis.gdal.error import OGRException
from django.contrib.gis.geos.error import GEOSException

from komoo_map.models import GeoRefModel
from main.utils import to_json
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
    row_dict = obj.row_dict['Contato']

    contacts = ContactsField.defaults()
    contacts['address'] = "%s, %s - %s" % (row_dict['Endereço'],
                                           row_dict['Número'],
                                           row_dict['Bairro'])
    contacts['compl'] = row_dict['Complemento']
    contacts['postal_code'] = row_dict['CEP']
    contacts['city'] = "%s / %s" % (row_dict['Município'], row_dict['UF'])
    contacts['phone'] = "(%s) %s" % (row_dict['DDD'], row_dict['Telefone'])
    contacts['email'] = row_dict['E-mail']

    obj.object_dict['contacts'] = contacts


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
            link=ref['Link'], link_title=ref['Título do link'],
            date=ref['Data']), refs)

    c = Context({
        'sections': sections,
        'references': refs,
    })
    t = Template('''\
{% for title, text in sections.items %}
{% if text %}### {{ title }}
{{ text|safe }}{% endif %}
{% endfor %}
{% if references %}### Referências{% endif %}
{% for r in references %}\
 - {% if r.author %}{{r.author}}: {% endif %}{% if r.link %}[{{r.source}}]({{r.link|safe}} "{{r.link_title}}"){% endif %}{% if r.date %}, consultado em {{r.date}}{% endif %}
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


def set_geometria(obj):
    gd = obj.row_dict['Geometria']
    point = gd.get('Ponto')
    point_as_area = gd.get('Ponto como área')
    from_kml = gd.get('Identificador do polígono (KML)') if obj.kml_dicts else None

    num_geometries = len([v for v in [point, point_as_area, from_kml] if v])
    if num_geometries == 0:
        return  # nothing to do!
    if num_geometries > 1:
        msg = 'Mais de uma geometria definida. Defina somente a coluna "Ponto",'\
              'ou "Ponto como Área", ou "Identificador do polígono (KML)"'
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
        elif from_kml: # Polygon or MultiLineString
            found = False
            for kd in obj.kml_dicts:
                if from_kml == kd['Identificador do polígono']:
                    found = True
                    if 'type' in kd['Geometria'] and \
                    kd['Geometria']['type'] == 'GeometryCollection':
                        if kd['Geometria']['geometries'][0]['type'] == 'LineString':
                            # we got geometry collection with some linestrings
                            # lets crate a `MultiLineString` geometry
                            coords = [geom['coordinates'] \
                                        for geom in kd['Geometria']['geometries']]
                            geodict['geometries'] = [{
                                'type': 'MultiLineString',
                                'coordinates': coords  # put many linestrings together
                            }]
                        else:
                            # if we dont got linestrings, assume that this is a polygon
                            coords = [geom['coordinates'][0] \
                                        for geom in kd['Geometria']['geometries']]
                            geodict['geometries'] = [{
                                'type': 'Polygon',
                                'coordinates': coords  # put many polygons together
                            }]
                    else:  # only 1 polygon
                        geodict['geometries'] = [kd['Geometria']['geometry']]

                    # FIXME: correct order is lat, lng. Before fixing must adjust
                    #        both in DB and in the map.
                    def fixcoords(data):
                        if isinstance(data, list) and isinstance(data[0], float):
                            # swap coords and chomp possible z axis.
                            return [data[1], data[0]]
                        if isinstance(data, list):
                            for i in range(len(data)):
                                data[i] = fixcoords(data[i])
                        if isinstance(data, dict):
                            for k, v in data.items():
                                data[k] = fixcoords(v)
                        return data

                    geodict = fixcoords(geodict)

                    break
            if not found:
                msg = 'Identificador do polígono não encontrado: {}'.format(from_kml)
                obj.errors.append(msg)
                return

        g = GeoRefModel()
        geojson = to_json(geodict)
        g.geometry = geojson
        obj.object_dict['geometry'] = geojson
        obj.object_dict['geometry_preview'] = point or point_as_area or from_kml or ''

    except ValueError:
        msg = 'Dado de geometria não é um número válido.'
        obj.errors.append(msg)

    except OGRException as e:
        msg = 'Má formação da(s) coluna(s) de geometria.'
        obj.errors.append(msg)

    except GEOSException as e:
        msg = 'Informação geométrica inconsistente.'
        obj.errors.append(msg)


def set_tags(obj):
    obj.object_dict['tags'] = map(lambda tag: tag.lower(),
        filter(bool, obj.row_dict['Palavras-chave'].values()))
    # TODO: put similar tags in the warnings dict

    # Data qualification tags
    if 'Contato' in obj.row_dict:
        if not obj.row_dict['Contato']['CEP']:
            obj.object_dict['tags'].append('sem CEP')
        if not obj.row_dict['Contato']['Telefone']:
            obj.object_dict['tags'].append('sem telefone')
        if not obj.row_dict['Contato']['E-mail']:
            obj.object_dict['tags'].append('sem e-mail')
    if not bool([s for s in obj.row_dict['Geometria'].values() if s != '']):
        obj.object_dict['tags'].append('sem ponto')
    if obj.row_dict['Geometria']['Ponto como área'] != '':
        obj.object_dict['tags'].append('ponto aproximado')

    for t in obj.object_dict['tags']:
        if len(t) > 100:
            msg = 'Tag excede 100 caracteres: {}'.format(t)
            obj.errors.append(msg)

