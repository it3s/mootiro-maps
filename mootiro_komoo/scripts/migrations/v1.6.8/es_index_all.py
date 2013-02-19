# -*- coding: utf-8 -*-
from organization.models import Organization
from komoo_resource.models import Resource
from need.models import Need
from community.models import Community
from authentication.models import User
from komoo_project.models import Project
from search.utils import index_object

model_list = [Organization, Resource, Need, Community, User, Project]

for model in model_list:
    for obj in model.objects.all():
        index_object(obj)


