# -*- coding: utf-8 -*-

from komoo_resource.models import Resource
from organization.models import Organization
from community.models import Community

def migrate_community_relations():
    for model in [Resource, Organization]:
        for obj in model.objects.all():
            # TODO implement-me
            # obj -> community  <= -contains
            pass

def run():
    migrate_community_relations()


