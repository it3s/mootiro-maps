# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import Context, Template
from django.utils.translation import ugettext as _

from komoo_resource.models import Resource, ResourceKind

from .base import Interpreter, RowInterpreter
import helpers


class RecursosRowInterpreter(RowInterpreter):

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
           self.row_dict['Nome']['Nome do recurso']:
            self.object_dict['name'] = '{} - {}' \
                    .format(self.row_dict['Nome']['Nome do recurso'],
                            self.row_dict['Nome']['Sigla'])
        else:
            self.object_dict['name'] = self.row_dict['Nome']['Nome do recurso']

        # == Contato ==
        helpers.set_contato(self)

        # == Descrição ==
        helpers.set_descricao(self)

        # == Comunidades ==
        helpers.set_comunidades(self)

        # == Tipo ==
        od['kind'] = rd['Tipo']

        # == Geometria ==
        helpers.set_geometria(self)

        # == Palavras-chave ==
        helpers.set_tags(self)

        # Duplicates
        # TODO: inexact title search for warnings
        # TODO: use georef to enhance matches
        q = Resource.objects.filter(name=od['name'])
        if q.exists():
            obj = q[0]
            self.errors.append('Já existe um recurso com este nome. (ID: {0})'\
                    .format(obj.id))

        # Missing Values
        if not od['name']:
            self.errors.append('Coluna "Nome do recurso" não pode estar vazia.')
        if not od['description']:
            self.errors.append('Coluna "Descrição" não pode estar vazia.')

    def to_object(self):
        if hasattr(self, 'object') and self.object:
            return self.object

        d = self.object_dict
        r = Resource()
        for attr in ['name', 'creator', 'contact', 'description']:
            setattr(r, attr, d[attr])
        if 'geometry' in d:
            r.geometry = d['geometry']
        q = ResourceKind.objects.filter(name=d['kind'])
        if q.count() > 1:  # this *should* be not necessary!
            r.kind = q[0]
        else:
            r.kind, created = ResourceKind.objects \
                                    .get_or_create(name=d['kind'])
        r.save()
        
        # m2m relationships
        r.community = d['community']
        r.tags.add(*d['tags'])
        r.save()

        self.object = r
        return r


class RecursosInterpreter(Interpreter):
    '''
    A model of this worksheet is public available in:
    https://docs.google.com/spreadsheet/ccc?key=0Ahdnyvg2LXX-dHNVTHB6ZGgtVGw3dzVOMVMtV01KWWc#gid=4
    '''
    header_rows = 2
    worksheet_name = 'Recursos'
    row_interpreter = RecursosRowInterpreter
    row_template = 'importsheet/row_templates/recursos.html'
