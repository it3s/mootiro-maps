# -*- coding: utf8 -*-
from __future__ import unicode_literals

from django.template import Context, Template

from authentication.models import User
from apps.organization.models import Organization
from apps.organization.models import OrganizationCategoryTranslation
from apps.organization.models import TargetAudience
from resources.models import Resource

from .base import Interpreter


class OrganizationInterpreter(Interpreter):
    '''
    A model of this worksheet is public available in:
    https://docs.google.com/spreadsheet/ccc?key=
    '''
    header_rows = 2
    # TODO: change this name
    worksheet_name = 'organization'
    
    def row_dict_to_object(self, row_dict):

        rd = row_dict

        d = {}
        e = {}
        w = {}

        # == Controle ==
        d['id'] = rd['Controle']['ID']
        d['type'] = {
            'organização': Organization,
            'recurso': Resource,
        }[rd['Controle']['Tipo'].lower()]
        try:
            d['creator'] = User.objects.get(name=rd['Controle']['Nome do mapeador'])
        except:
            d['creator'] = None

        # == Nome ==
        if rd['Nome']['Sigla'] and rd['Nome']['Nome da organização']:
            d['name'] = '{} - {}'.format(rd['Nome']['Sigla'],
                                    rd['Nome']['Nome da organização'])
        else:
            d['name'] = rd['Nome']['Nome da organização']

        # == Contato ==
        contact = rd['Contato']
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
            'website': contact['Website'],
        })
        t = Template('''
{% if address %}**Endereço:** {{address}}, {{number}}{% if complement %}, {{complement}}{% endif %} - {{district}}
{% if zipcode %}CEP: {{zipcode}}, {% endif %}{{city}}/{{state}}{% endif %}

{% if phone_number %}**Telefone:** {% if area_code %}({{area_code}}){% endif %} {{phone_number}}{% endif %}

{% if email %}**E-mail:** {{email}}{% endif %}

{% if website %}**Website:** {{website}}{% endif %}
''')
        d['contact'] = t.render(c)

        # == Description ==
        sections = rd['Descrição']
        for title in sections:  # do not use dict comprehension
            if not sections[title]:
                sections.pop(title)
        # clean and map references dicts
        refs = [rd['Referência 1'], rd['Referência 2'], rd['Referência 3']]
        refs = filter(lambda r: bool([v for v in r.values() if v]), refs)
        refs = map(lambda ref: dict(author=ref['Autor'], source=ref['Fonte'], 
                link=ref['Link'], link_title=ref['Título do link'], date=ref['Data']), refs)
        c = Context({
            'sections': rd['Descrição'],
            'references': refs,
        })
        t = Template('''
{% for title, text in sections.items %}
{% if text %}#### {{ title }}
{{ text }}{% endif %}
{% endfor %}

{% if references %}#### Referências{% endif %}
{% for r in references %}
 - {% if r.author %}{{r.author}}: {% endif %}{% if r.link %}[{{r.source}}]({{r.link}} "{{r.link_title}}"){% endif %}{% if r.date %}, consultado em {{r.date}}{% endif %}
{% endfor%}
''')
        d['description'] = t.render(c)

        # == Coordenadas ==
        print rd.keys()
        lat = rd['Coordenadas do ponto']['Latitude']
        lng = rd['Coordenadas do ponto']['Longitude']
        if lat and lng:
            d['geometry'] = 'POINT(%s, %s)' % (lat, lng)
        
        # == Categorias ==
        provided = set(filter(bool, rd['Categorias'].values()))
        valid = OrganizationCategoryTranslation.objects.filter(name__in=provided)
        valid = set([c.category.name for c in valid])
        invalid = provided - valid
        if invalid:
            e['invalid_categories'] = invalid
        d['categories'] = valid

        # == Palavras-chave ==
        d['tags'] = filter(bool, rd['Palavras-chave'].values())
        # TODO: put similar tags in the warnings dict

        # == Públicos-alvo ==
        d['target_audiences'] = filter(bool, rd['Públicos-alvo'].values())
        # TODO: put similar target audiences in the warnings dict        

        o = d['type'].from_dict(d)
        if o.is_valid():
            pass
        else:
            e.update(o.errors)
        w = {}

        # Duplicates
        # TODO: inexact title search
        # TODO: use georef to enhance matches
        q = d['type'].objects.filter(name=d['name'])
        if q.exists():
            w['duplicates'] = []
            for obj in q:
                w['duplicates'].append(obj)

        return {'object': o, 'warnings': w, 'errors': e}
