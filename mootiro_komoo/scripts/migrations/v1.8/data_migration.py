# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from komoo_resource.models import Resource
from main.models import GeoRefObject


def migrate_resources():
    for res in Resource.objects.all():
        o = GeoRefObject()
        o.otype = 'resource'
        o.name = res.name
        o.description = res.description
        o.description += res.contact
        o.contact = {}
        o.creator = res.creator
        o.creation_date = res.creation_date
        o.last_editor = res.last_editor
        o.last_update = res.last_update
        o.geometry = res.geometry

        o.tags = {
            # 'resource type': res.resourcekind_set.all()
            # 'common_namespace': res.tags
        }

        # o.relations.add(com) for com in res.community_set.all()

        # investments??
