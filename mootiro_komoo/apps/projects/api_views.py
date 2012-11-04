#! coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from main.utils import create_geojson

from organization.models import Organization
from projects.models import Project

from main.views import HybridDetailView

logger = logging.getLogger(__name__)


class ProjectItemView(HybridDetailView):
    template_name = 'project/view.html'
    model = Project
    slug_field = 'id'

    def convert_context_to_json(self, context):
        return self.object.json

    def get_context_data(self, **kwargs):
        context = super(ProjectItemView, self).get_context_data(**kwargs)

        if self.format == 'application/json':
            return context

        project = context['project']

        proj_objects, items = {}, []

        proj_objects['User'] = {
                'app_name': 'authentication',
                'objects_list': [{
                    'name': project.creator.name,
                    'link': project.creator.view_url,
                    'id': project.creator.id,
                    'has_geojson': bool(getattr(project.creator,
                        'geometry', ''))
                }]
            }

        for c in project.contributors.all():
            if c != project.creator:
                proj_objects['User']['objects_list'].append({
                    'name': c.name,
                    'link': c.view_url,
                    'id': c.id,
                    'has_geojson': bool(getattr(c, 'geometry', ''))
                })

        for p in project.related_objects:
            obj = p.content_object
            if obj:
                if not proj_objects.get(obj.__class__.__name__, None):
                    proj_objects[obj.__class__.__name__] = {
                            'app_name': obj.__module__.split('.')[0],
                            'objects_list': []
                        }
                proj_objects[obj.__class__.__name__]['objects_list'].append({
                    'name': obj.name.strip(),
                    'link': obj.view_url,
                    'id': obj.id,
                    'has_geojson': bool(getattr(obj, 'geometry', ''))
                })

                if isinstance(obj, Organization):
                    branchs = [b for b in obj.organizationbranch_set.all()]
                    if branchs:
                        items += branchs
                else:
                    items.append(obj)
        geojson = create_geojson(items)

        # ugly sort
        for key in proj_objects.iterkeys():
            proj_objects[key]['objects_list'].sort(key=lambda o: o['name'])

        context['geojson'] = geojson
        context['proj_objects'] = proj_objects

        return context

