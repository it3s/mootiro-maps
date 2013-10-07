# -*- coding: utf-8 -*-
from celery.task import task
from model_versioning.models import ModelVersion


@task
def versionate(table_ref, object_id, user_id, data):
    """Create ModelVersion"""
    ModelVersion.create(table_ref=table_ref, object_id=object_id, user_id=user_id, data=data)
