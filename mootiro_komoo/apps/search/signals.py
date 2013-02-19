# -*- coding: utf-8 -*-
import django.dispatch
from django.dispatch import receiver
from celery.task import task
from .utils import index_object, es_index_dict


index_object_for_search = django.dispatch.Signal(providing_args=["obj", ])


@task
def _index_object_task(obj_data):
    index_object(obj_data)


@receiver(index_object_for_search)
def index_object_callback(sender, obj, *a, **kw):
    if getattr(obj, 'id', None):
        obj_data = es_index_dict(obj)
        _index_object_task.delay(obj_data)

