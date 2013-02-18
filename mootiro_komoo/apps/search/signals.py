# -*- coding: utf-8 -*-
import django.dispatch
from django.dispatch import receiver
from .utils import index_object


index_object_for_search = django.dispatch.Signal(providing_args=["obj", ])


@receiver(index_object_for_search)
def index_object_callback(sender, obj, *a, **kw):
    print 'INDEXING', obj
    # index_object(obj)

