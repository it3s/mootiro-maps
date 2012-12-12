# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import Context, Template
from django.utils.translation import ugettext as _

from community.models import Community

from .base import Interpreter, RowInterpreter
import helpers


class ComunidadesRowInterpreter(RowInterpreter):

    def parse(self):
        # references to same objects
        self.object_dict = {}
        self.errors = []
        self.warnings = []

        # == Controle ==
        helpers.set_controle(self)

        # == Nome ==
        if self.row_dict['Nome']['Detalhe'] and \
           self.row_dict['Nome']['Nome da comunidade']:
            self.object_dict['name'] = '{} ({})' \
                    .format(self.row_dict['Nome']['Nome da comunidade'],
                            self.row_dict['Nome']['Detalhe'])
        else:
            self.object_dict['name'] = self.row_dict['Nome']['Nome da comunidade']

        # == População ==
        if self.row_dict['População']:
            try:
                self.object_dict['population'] = int(self.row_dict['População'])
            except:
                msg = 'População inválida: {} não é um número inteiro.' \
                            .format(self.row_dict['População'])
                self.errors.append(msg)

        # == Descrição ==
        helpers.set_descricao(self)

        # == Geometria ==
        helpers.set_geometria(self)
        if not self.object_dict.get('geometry', None):
            msg = 'Comunidades devem ter uma geometria definida.'
            self.errors.append(msg)

        # == Palavras-chave ==
        helpers.set_tags(self)

        # Duplicates
        # TODO: inexact title search for warnings
        # TODO: use georef to enhance matches
        q = Community.objects.filter(name=self.object_dict['name'])
        if q.exists():
            obj = q[0]
            self.errors.append('Já existe uma comunidade com este nome. (ID: {0})'\
                    .format(obj.id))

        # Missing Values
        if not self.object_dict['name']:
            self.errors.append('Coluna "Nome dacomunidade" não pode estar vazia.')
        if not self.object_dict['description']:
            self.errors.append('Coluna "Descrição" não pode estar vazia.')

    def to_object(self):
        if hasattr(self, 'object') and self.object:
            return self.object

        d = self.object_dict
        c = Community()
        for attr in ['name', 'creator', 'description', 'geometry']:
            setattr(c, attr, d[attr])
        if 'population' in d:
            c.population = d['population']
        c.save()
        
        # m2m relationships
        c.tags.add(*d['tags'])
        c.save()

        self.object = c
        return c


class ComunidadesInterpreter(Interpreter):
    '''
    A model of this worksheet is public available in:
    https://docs.google.com/spreadsheet/ccc?key=0Ahdnyvg2LXX-dHNVTHB6ZGgtVGw3dzVOMVMtV01KWWc#gid=6
    '''
    header_rows = 2
    worksheet_name = 'Comunidades'
    row_interpreter = ComunidadesRowInterpreter
    row_template = 'importsheet/row_templates/comunidades.html'
