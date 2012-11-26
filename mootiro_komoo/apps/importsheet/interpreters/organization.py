# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import Context, Template
from django.utils.translation import ugettext as _

from authentication.models import User
from apps.organization.models import Organization
from apps.organization.models import OrganizationBranch
from apps.organization.models import OrganizationCategoryTranslation
from apps.organization.models import TargetAudience
from komoo_resource.models import Resource

from .base import Interpreter


class OrganizationInterpreter(Interpreter):
    '''
    A model of this worksheet is public available in:
    https://docs.google.com/spreadsheet/ccc?key=
    '''
    header_rows = 2
    worksheet_name = 'Organizações'
    
    def row_dict_to_parse_dict(self, row_dict):
        rd = row_dict
        # parse_dict information
        d = {}
        e = {}
        w = {}

        # == Controle ==
        d['id'] = rd['Controle']['ID']
        try:
            d['creator'] = User.objects.get(id=rd['Controle']['ID do mapeador'])
        except:
            msg = _('Invalid creator ID: {} does not belong to any user.'.format(rd['Controle']['ID do mapeador']))
            e['invalid_creator'] = msg

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
        })
        t = Template('''
{% if address %}**Endereço:** {{address}}, {{number}}{% if complement %}, {{complement}}{% endif %} - {{district}}
{% if zipcode %}CEP: {{zipcode}}, {% endif %}{{city}}/{{state}}{% endif %}

{% if phone_number %}**Telefone:** {% if area_code %}({{area_code}}){% endif %} {{phone_number}}{% endif %}

{% if email %}**E-mail:** {{email}}{% endif %}
''')
        d['link'] = contact['Website']
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
        lat = rd['Coordenadas do ponto']['Latitude']
        lng = rd['Coordenadas do ponto']['Longitude']
        if lat and lng:
            d['geometry'] = 'POINT(%s, %s)' % (lat, lng)
        
        # == Categorias ==
        provided = set(filter(bool, rd['Categorias'].values()))
        valid = OrganizationCategoryTranslation.objects.filter(name__in=provided)
        valid = set([c.name for c in valid])
        invalid = provided - valid
        if invalid:
            msg = _('Invalid categories: ') + ', '.join(invalid)
            e['invalid_categories'] = msg
        d['categories'] = valid

        # == Palavras-chave ==
        d['tags'] = filter(bool, rd['Palavras-chave'].values())
        # TODO: put similar tags in the warnings dict

        # Data qualification tags
        if not contact['CEP']:
            d['tags'].append('sem CEP')
        if not contact['Telefone']:
            d['tags'].append('sem telefone')
        if not contact['E-mail']:
            d['tags'].append('sem e-mail')
        if not lat or not lng:
            d['tags'].append('sem ponto')

        # == Públicos-alvo ==
        d['target_audiences'] = filter(bool, rd['Públicos-alvo'].values())
        # TODO: put similar target audiences in the warnings dict        

        # Duplicates
        # TODO: inexact title search for warnings
        # TODO: use georef to enhance matches
        q = Organization.objects.filter(name=d['name'])
        if q.exists():
            obj = q[0]
            e['duplicate'] = _('There is already an organization with this name.')

        # Missing Values
        for attr in ['name', 'description']:
            if not d[attr]:
                e[attr] = '%s cannot be empty' % attr

        return {'object_dict': d, 'warnings': w, 'errors': e}

    def object_dict_to_object(self, d):

        o = Organization()
        for attr in ['name', 'creator', 'contact', 'link', 'description']:
            setattr(o, attr, d[attr])
        o.save()
        
        # m2m relationships
        octs = OrganizationCategoryTranslation.objects \
                    .filter(name__in=d['categories'])
        o.categories = [c.category for c in octs]

        o.tags.add(*d['tags'])

        o.target_audiences = [TargetAudience.objects.get_or_create(name=ta)[0]\
                                for ta in d['target_audiences']]

        if 'geometry' in d:
            br = OrganizationBranch(name='Sede', creator=d['creator'],
                    organization=o)
            br.save()
        o.save()

        return o
