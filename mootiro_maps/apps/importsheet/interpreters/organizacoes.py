# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import Context, Template
from django.utils.translation import ugettext as _

from apps.organization.models import Organization
from apps.organization.models import OrganizationCategoryTranslation
from apps.organization.models import TargetAudience

from .base import Interpreter, RowInterpreter
import helpers


class OrganizacoesRowInterpreter(RowInterpreter):

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
           self.row_dict['Nome']['Nome da organização']:
            self.object_dict['name'] = '{} - {}' \
                    .format(self.row_dict['Nome']['Nome da organização'],
                            self.row_dict['Nome']['Sigla'])
        else:
            self.object_dict['name'] = self.row_dict['Nome']['Nome da organização']

        # == Contato ==
        helpers.set_contato(self)
        self.object_dict['link'] = self.row_dict['Contato']['Website']

        # == Descrição ==
        helpers.set_descricao(self)

        # == Comunidades ==
        helpers.set_comunidades(self)

        # == Geometria ==
        helpers.set_geometria(self)

        # == Palavras-chave ==
        helpers.set_tags(self)

        # == Categorias ==
        provided = set(filter(bool, rd['Categorias'].values()))
        valid = OrganizationCategoryTranslation.objects.filter(name__in=provided)
        valid = set([c.name for c in valid])
        invalid = provided - valid
        if invalid:
            msg = _('Invalid categories: ') + ', '.join(invalid)
            self.errors.append(msg)
        od['categories'] = valid

        # == Públicos-alvo ==
        od['target_audiences'] = filter(bool, rd['Públicos-alvo'].values())
        # TODO: put similar target audiences in the warnings dict

        # Duplicates
        # TODO: inexact title search for warnings
        # TODO: use georef to enhance matches
        q = Organization.objects.filter(name=od['name'])
        if q.exists():
            obj = q[0]
            self.errors.append('Já existe uma organização com este nome. '\
                    ' (ID: {0})'.format(obj.id))

        # Missing Values
        if not od['name']:
            self.errors.append('Coluna "Nome da organização" não pode estar vazia.')
        if not od['description']:
            self.errors.append('Coluna "Descrição" não pode estar vazia.')


    def to_object(self):

        if hasattr(self, 'object') and self.object:
            return self.object

        d = self.object_dict
        o = Organization()
        for attr in ['name', 'creator', 'contacts', 'link', 'description']:
            setattr(o, attr, d[attr])
        o.save()

        # m2m relationships
        o.community = d['community']
        octs = OrganizationCategoryTranslation.objects \
                    .filter(name__in=d['categories'])
        o.categories = [c.category for c in octs]
        o.tags.add(*d['tags'])
        o.target_audiences = [TargetAudience.objects.get_or_create(name=ta)[0]\
                                for ta in d['target_audiences']]

        if 'geometry' in d:
            o.geometry = d['geometry']
        o.save()

        self.object = o
        return o


class OrganizacoesInterpreter(Interpreter):
    '''
    A model of this worksheet is public available in:
    https://docs.google.com/spreadsheet/ccc?key=0Ahdnyvg2LXX-dG9PTUpXMzBGN2F5MWJxYWRDQXRScHc#gid=1
    '''
    header_rows = 2
    worksheet_name = 'Organizações'
    row_interpreter = OrganizacoesRowInterpreter
    row_template = 'importsheet/row_templates/organizacoes.html'
