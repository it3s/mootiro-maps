#! /usr/bin/env python
# -*- coding:utf-8 -*-
from fabric.state import env
from fabric.api import task
from .base import logging, virtualenv, setup_django


@task
def index_all():
    """ Reindex all objects """
    with virtualenv(), env.cd('mootiro_maps'):
        setup_django()

        from organization.models import Organization
        from komoo_resource.models import Resource
        from need.models import Need
        from community.models import Community
        from authentication.models import User
        from komoo_project.models import Project
        from search.utils import (reset_index,
                                  create_mapping,
                                  refresh_index,
                                  index_object)

        model_list = [Organization, Resource, Need, Community, User, Project]

        logging.info('Recreating index ... ')
        reset_index()

        logging.info('Create mappings ... ')
        create_mapping()

        logging.info('Indexing each object ... ')
        for model in model_list:
            for obj in model.objects.all():
                index_object(obj)

        logging.info('refreshing index ... ')
        refresh_index()

        logging.info('ES indexes rebuilt.')
