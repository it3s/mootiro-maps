# -*- coding: utf-8 -*-
from celery.task import task
from model_versioning.models import ModelVersion


@task
def versionate_async(table_ref, object_id, user_id, data):
    """Create ModelVersion"""
    version = ModelVersion(table_ref=table_ref, object_id=object_id, creator_id=user_id, data=data)
    version.save()

def versionate(user, obj):
  versionate_async(obj.table_ref, obj.id, user.id, obj.to_json())
