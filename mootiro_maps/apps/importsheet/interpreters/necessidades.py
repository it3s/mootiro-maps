# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import Context, Template
from django.utils.translation import ugettext as _

from apps.need.models import Need
from apps.need.models import NeedCategory
from apps.need.models import TargetAudience

from .base import Interpreter, RowInterpreter
import helpers


class NecessidadesRowInterpreter(RowInterpreter):

    def __init__(self, row_dict, kml_dicts):
        self.row_dict = row_dict
        self.kml_dicts = kml_dicts

    def parse(self):

        # references to same objects
        rd = self.row_dict
        od = self.object_dict = {}
        self.errors = []
        self.warnings = []

        # == Controle ==
        helpers.set_controle(self)

        # == Nome ==
        if self.row_dict['Nome']['Sigla'] and \
           self.row_dict['Nome']['Nome da necessidade']:
            self.object_dict['name'] = '{} - {}' \
                    .format(self.row_dict['Nome']['Nome da necessidade'],
                            self.row_dict['Nome']['Sigla'])
        else:
            self.object_dict['name'] = self.row_dict['Nome']['Nome da necessidade']

        # == Descrição ==
        helpers.set_descricao(self)

        # == Comunidades ==
        helpers.set_comunidades(self)

        # == Geometria ==
        helpers.set_geometria(self)

        # == Palavras-chave ==
        helpers.set_tags(self)

        # == Áreas ==
        provided = filter(bool, rd['Áreas'].values())
        provided = set(map(NeedCategory.backtrans, provided))
        valid_objs = NeedCategory.objects.filter(name__in=provided)
        valid = set([c.name for c in valid_objs])
        invalid = provided - valid
        if invalid:
            msg = _('Invalid need categories: ') + ', '.join(invalid)
            self.errors.append(msg)
        od['categories'] = valid_objs

        # == Públicos-alvo ==
        od['target_audiences'] = filter(bool, rd['Públicos-alvo'].values())
        # TODO: put similar target audiences in the warnings dict

        # Duplicates
        # TODO: inexact title search for warnings
        # TODO: use georef to enhance matches
        q = Need.objects.filter(name=od['name'])
        if q.exists():
            obj = q[0]
            self.errors.append('Já existe uma necessidade com este nome. '\
                    ' (ID: {0})'.format(obj.id))

        # Missing Values
        if not od['name']:
            self.errors.append('Coluna "Nome da necessidade" não pode estar vazia.')
        if not od['description']:
            self.errors.append('Coluna "Descrição" não pode estar vazia.')
        if not od['categories']:
            self.errors.append('Coluna "Áreas" não pode estar vazia.')
        if not od['target_audiences']:
            self.errors.append('Coluna "Públicos-alvo" não pode estar vazia.')

    def to_object(self):

        if hasattr(self, 'object') and self.object:
            return self.object

        d = self.object_dict
        n = Need()
        for attr in ['creator', 'description']:
            setattr(n, attr, d[attr])
        n.name = d['name']
        n.save()

        # m2m relationships
        n.community = d['community']
        n.categories = d['categories']
        n.tags.add(*d['tags'])
        n.target_audiences = [TargetAudience.objects.get_or_create(name=ta)[0]\
                                for ta in d['target_audiences']]

        if 'geometry' in d:
            n.geometry = d['geometry']
        n.save()

        self.object = n
        return n


class NecessidadesInterpreter(Interpreter):
    '''
    A model of this worksheet is public available in:
    https://docs.google.com/spreadsheet/ccc?key=0Ahdnyvg2LXX-dG9PTUpXMzBGN2F5MWJxYWRDQXRScHc#gid=8
    '''
    header_rows = 2
    worksheet_name = 'Necessidades'
    row_interpreter = NecessidadesRowInterpreter
    row_template = 'importsheet/row_templates/necessidades.html'
